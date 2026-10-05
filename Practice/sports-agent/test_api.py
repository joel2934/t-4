import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CRICKET_API_KEY")

if not API_KEY:
    raise ValueError(
        "CRICKET_API_KEY is missing from .env"
    )


url = "https://api.cricapi.com/v1/currentMatches"

params = {
    "apikey": API_KEY,
    "offset": 0
}


response = requests.get(
    url,
    params=params,
    timeout=10
)


print("Status code:", response.status_code)

response.raise_for_status()

data = response.json()

print("\nAPI Response:")
print(data)