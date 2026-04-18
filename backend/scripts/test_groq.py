import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_groq():
    key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    payload = {
        "model": "llama-3.1-8b-instant",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "user", "content": "Respond with a json object containing 'hello': 'world'. Use the keyword json."}
        ]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_groq())
