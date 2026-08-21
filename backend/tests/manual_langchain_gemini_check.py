import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
)

response = model.invoke(
    "You are CareerPilot AI. Explain what you can do for a software engineering student in two sentences."
)

print("RESPONSE OBJECT:")
print(response)
print("CONTENT:")
print(repr(response.content))