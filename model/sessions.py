from typing import Dict, List, Optional

# 전역 세션 관리
from fastapi import WebSocket

# 각 사용자별 독립적인 세션
class UserSession:
    def __init__(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.chat_history: List[Dict] = []
        self.websocket: Optional[WebSocket] = None
    
    def add_message(self, user: str, model: str):
        message = {"user_message" : user, "model_answer" : model}
        self.chat_history.append(message)
        return message

    def get_history(self):
        return [msg.to_dict() for msg in self.chat_history]
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "message_count": len(self.chat_history),
            "websocket_active": self.websocket is not None,
        }
    
    def __repr__(self):
        return f"UserSession(user_id={self.user_id}, user_name={self.user_name}, chat_history={self.chat_history})"
