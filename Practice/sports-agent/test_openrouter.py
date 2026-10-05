import os

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


load_dotenv()


print(
    "OpenRouter key loaded:",
    bool(os.getenv("OPENROUTER_API_KEY"))
)


llm = ChatOpenRouter(
    model="openrouter/free",
    temperature=0
)


response = llm.invoke(
    "Say hello in one sentence."
)


print("\nAI RESPONSE:")
print(response.content)