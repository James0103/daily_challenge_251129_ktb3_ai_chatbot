import os, asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

async def send_message_stream(message: str):
    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash")
    try:
        response = chat.send_message_stream(message)
        for chunk in response:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.2)
    except Exception as e:
        yield f"Error: {str(e)}"
