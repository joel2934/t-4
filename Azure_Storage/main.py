import asyncio
import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions,
)

# Load AZURE_STORAGE_CONNECTION_STRING / AZURE_STORAGE_CONTAINER from a local .env file (if present)
load_dotenv()

app = FastAPI(title="SecureShare - Azure Blob SAS Demo")

CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER")

if not CONNECTION_STRING or not CONTAINER_NAME:
    raise RuntimeError(
        "Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER. "
        "Set them as environment variables (locally in a .env file, "
        "or as Application Settings once deployed to Azure)."
    )

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Make sure the container exists (safe to call even if it already does)
try:
    container_client.create_container()
except Exception:
    pass  # already exists

# --- In-memory self-destruct tracking -----------------------------------
# NOTE: this lives only in this running process's memory. It resets if the
# server restarts (e.g. uvicorn --reload picking up a code change). For a
# real production "auto-delete" feature you'd instead use Azure Blob
# Storage lifecycle management rules (day-granularity) or a small Azure
# Function on a timer trigger — this in-process version exists purely to
# make a short, dramatic classroom demo (minute/second granularity).
self_destruct_tasks: dict[str, asyncio.Task] = {}
self_destruct_times: dict[str, datetime] = {}


async def _delayed_delete(blob_name: str, delay_seconds: float):
    try:
        await asyncio.sleep(delay_seconds)
        container_client.get_blob_client(blob_name).delete_blob()
    except asyncio.CancelledError:
        pass
    except Exception:
        pass
    finally:
        self_destruct_tasks.pop(blob_name, None)
        self_destruct_times.pop(blob_name, None)


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file straight from the browser into the Azure Blob container."""
    blob_client = container_client.get_blob_client(file.filename)
    contents = await file.read()
    blob_client.upload_blob(contents, overwrite=True)
    return {"message": f"'{file.filename}' uploaded successfully."}


@app.get("/files")
async def list_files():
    """List every blob currently in the container, with self-destruct status if scheduled."""
    files = []
    for b in container_client.list_blobs():
        entry = {"name": b.name}
        if b.name in self_destruct_times:
            entry["self_destructs_at_utc"] = self_destruct_times[b.name].strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        files.append(entry)
    return {"files": files}


@app.get("/generate-link/{blob_name}")
async def generate_link(blob_name: str, minutes_valid: int = 5):
    """Generate a time-limited (SAS) read-only URL for one blob."""
    blob_client = container_client.get_blob_client(blob_name)
    if not blob_client.exists():
        raise HTTPException(status_code=404, detail=f"'{blob_name}' not found.")

    account_name = blob_service_client.account_name
    account_key = blob_service_client.credential.account_key
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time,
    )

    url = (
        f"https://{account_name}.blob.core.windows.net/"
        f"{CONTAINER_NAME}/{blob_name}?{sas_token}"
    )

    return JSONResponse(
        {
            "url": url,
            "expires_at_utc": expiry_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "minutes_valid": minutes_valid,
        }
    )


@app.post("/self-destruct/{blob_name}")
async def schedule_self_destruct(blob_name: str, minutes: float = 2):
    """Schedule a blob to be permanently deleted after `minutes` from now."""
    blob_client = container_client.get_blob_client(blob_name)
    if not blob_client.exists():
        raise HTTPException(status_code=404, detail=f"'{blob_name}' not found.")

    # Replace any existing schedule for this blob
    existing_task = self_destruct_tasks.get(blob_name)
    if existing_task:
        existing_task.cancel()

    destruct_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    self_destruct_times[blob_name] = destruct_at
    self_destruct_tasks[blob_name] = asyncio.create_task(
        _delayed_delete(blob_name, minutes * 60)
    )

    return {
        "blob_name": blob_name,
        "self_destructs_at_utc": destruct_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "minutes": minutes,
    }


@app.post("/cancel-self-destruct/{blob_name}")
async def cancel_self_destruct(blob_name: str):
    """Cancel a previously scheduled self-destruct for a blob."""
    task = self_destruct_tasks.pop(blob_name, None)
    self_destruct_times.pop(blob_name, None)
    if not task:
        raise HTTPException(
            status_code=404, detail="No scheduled self-destruct for this file."
        )
    task.cancel()
    return {"message": f"Self-destruct canceled for '{blob_name}'."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
