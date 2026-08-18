import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000),
)

print("Calling Gemini...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Reply with exactly: CareerPilot AI is online.",
)

print("Gemini response:")
print(response.text)