from dotenv import load_dotenv
import os
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import init_db

from routes.chat import router as chat_router
from routes.conversations import router as conversations_router
from routes.upload import router as upload_router


app = FastAPI()

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

Path("uploads").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Initialize database
init_db()


# Register routes
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(upload_router)

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


@app.get("/")
async def home():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {
        "message": "BoxGPT is running"
    }


if __name__ == "__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8080,reload=True)
