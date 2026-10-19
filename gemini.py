from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Explain artificial intelligence in a simple sentence"
    )
    print(response.text)
except Exception as error:
    print("Gemini API error:", error)