import os
from dotenv import load_dotenv

load_dotenv()

print("CRICKET_API_KEY loaded:",
      bool(os.getenv("CRICKET_API_KEY")))

print("OPENAI_API_KEY loaded:",
      bool(os.getenv("OPENAI_API_KEY")))

