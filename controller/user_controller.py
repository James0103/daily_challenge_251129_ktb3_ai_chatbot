import uuid

def make_user_uuid(user_name: str) -> dict[str, str]:
  user_id = str(uuid.uuid4())
  return {
    "user_name": user_name,
    "user_id": user_id
  }