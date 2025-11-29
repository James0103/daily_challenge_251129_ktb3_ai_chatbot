from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from controller.gemini_controller import send_message_stream
from controller.user_controller import make_user_uuid
from model.models import UserModel
from model.sessions import UserSession
import json
from typing import Dict


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

# 세션 관리
user_sessions: Dict[str, UserSession] = {}
active_websockets: Dict[str, WebSocket] = {}

# 백엔드 유저 등록
@app.post("/register-user")
def register_user(user: UserModel) -> JSONResponse:  
  user_data = make_user_uuid(user_name=user.user_name)
  user_id = user_data["user_id"]
    # 사용자 세션 생성
  session = UserSession(user_id=user_id, user_name=user.user_name)
  user_sessions[user_id] = session

  return JSONResponse(user_data)

# 사용자 채팅 기록
@app.get("/api/history/{user_id}")
async def get_user_history(user_id: str) -> JSONResponse:
  if user_id not in user_sessions:
      return {"error": "User not found"}
  
  session = user_sessions[user_id]
  history = [
    {
        "user": session.chat_history[i]["user_message"],
        "gemini": session.chat_history[i + 1]["model_answer"]
    }
    for i in range(0, len(session.chat_history), 2)
  ]

  return JSONResponse({
    "user_id": user_id,
    "user_name": session.user_name,
    "message_count": len(history),
    "history": history
  })


# 웹소켓 부분
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  user_id = None
  user_name = None
  session = None

  try:
    while True:
      raw_text = await websocket.receive_text()
      data = json.loads(raw_text)
      
      if data.get('type') == 'init':
        # 초기화
        user_id = data.get('user_id')
        user_name = data.get('user_name')

        # WebSocket을 세션에 연결
        if user_id in user_sessions:
          session = user_sessions[user_id]
          session.websocket = websocket
          active_websockets[user_id] = websocket
          
          print(f"👤 [WS] User connected: {user_name} (ID: {user_id})")
          print(f"📊 [WS] Active connections: {len(active_websockets)}")
        
          # 기존 히스토리가 있으면 알림
          if session.chat_history:
            print(f"📚 [WS] User {user_id} has {len(session["chat_history"])} messages in history")
        else:
          print(f"⚠️ [WS] Unknown user_id: {user_id}")
      
      elif data.get('type') == 'message':
        message = data.get('content')
        # 2. 스트리밍 시작 신호
        await websocket.send_json({"type": "start"})

        async for chunk in send_message_stream(user_id, message, session):
          await websocket.send_json({
            "type": "chunk",
            "content": chunk
          })
        
        # 4. 스트리밍 완료 신호
        await websocket.send_json({"type": "end"})
  except WebSocketDisconnect:
    print(f"[WS] User {user_id} disconnected")
  except Exception as e:
    print(f"[WS ERROR] {e}")
    await websocket.close()
      