"""
PulseCheck — a live classroom polling app backed by Azure SQL Database.

Real use: run this during your own AZ-900 sessions. Ask a question out loud,
students vote from their phones, and everyone watches the results bar chart
fill in live — reading straight from real INSERT + GROUP BY queries against
Azure SQL, which is the actual teaching point underneath the fun.
"""

from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Vote, get_db, init_db

app = FastAPI(title="PulseCheck - Live Classroom Poll (Azure SQL Database)")

# Swap this out to run a new question in your next session.
QUESTION = "Which of these is a PaaS (Platform as a Service) offering in Azure?"
OPTIONS = ["Azure App Service", "Virtual Machines", "Azure Portal", "ExpressRoute"]

init_db()


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/poll")
async def get_poll():
    return {"question": QUESTION, "options": OPTIONS}


@app.post("/vote")
async def cast_vote(option: str = Form(...), db: Session = Depends(get_db)):
    if option not in OPTIONS:
        return {"error": "Invalid option"}
    db.add(Vote(option_text=option))
    db.commit()
    return {"message": "Vote recorded"}


@app.get("/results")
async def get_results(db: Session = Depends(get_db)):
    rows = (
        db.query(Vote.option_text, func.count(Vote.id))
        .group_by(Vote.option_text)
        .all()
    )
    counts = {option: 0 for option in OPTIONS}
    for option_text, count in rows:
        if option_text in counts:
            counts[option_text] = count
    total = sum(counts.values())
    return {"counts": counts, "total": total}


@app.post("/reset")
async def reset_votes(db: Session = Depends(get_db)):
    """Instructor-only in spirit — clears all votes to run the poll again."""
    db.query(Vote).delete()
    db.commit()
    return {"message": "Votes reset"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
