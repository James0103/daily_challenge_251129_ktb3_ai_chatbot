import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

app = FastAPI()

# 프론트엔드 파일 서빙
@app.get("/")
def index():
  return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

# 웹소켓 부분
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  while True:
      data = await websocket.receive_text()
      await websocket.send_text(f"Message text was: {data}")