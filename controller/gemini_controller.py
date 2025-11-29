import os, asyncio
from dotenv import load_dotenv
from google import genai
from model.sessions import UserSession

load_dotenv()

async def send_message_stream(user_id: str, message: str, user_sessions: UserSession):
    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash")
    
    try:
        user_sessions.add_message(user=message, model="")
        response = chat.send_message_stream(message)
        full_response = ""

        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
                await asyncio.sleep(0.2)
        
        user_sessions.add_message(user="", model=full_response)
    except Exception as e:
        yield f"Error: {str(e)}"
