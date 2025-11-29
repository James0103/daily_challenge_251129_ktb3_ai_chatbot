from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI()

@app.get("/")
def index():
    return PlainTextResponse("Daily Challenge", status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)