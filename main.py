from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from controller.gemini_controller import send_message_stream

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# 프론트엔드 파일 서빙
@app.get("/")
def index(request: Request):
  return templates.TemplateResponse(
     "index.html",
     {
      "request": request,
      "websocket_url": f"ws://{request.url.netloc}/ws"
     }
  )

# 웹소켓 부분
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  while True:
      data = await websocket.receive_text()
      async for chunk in send_message_stream(data):
        await websocket.send_json({
          "type": "chunk",
          "content": chunk
        })
      
      