import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database import engine
from models import Artwork, Bid, User
from models.base import Base
from routers import artworks, auth, bids, users

app = FastAPI(title="Guess The Worth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=settings.allowed_origins)

socket_app = socketio.ASGIApp(sio, app)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(artworks.router, prefix="/api/artworks", tags=["artworks"])
app.include_router(bids.router, prefix="/api/bids", tags=["bids"])


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Guess The Worth API"}


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def join_artwork(sid, data):
    artwork_id = data.get("artwork_id")
    await sio.enter_room(sid, f"artwork_{artwork_id}")
    print(f"Client {sid} joined artwork {artwork_id}")


@sio.event
async def leave_artwork(sid, data):
    artwork_id = data.get("artwork_id")
    await sio.leave_room(sid, f"artwork_{artwork_id}")
    print(f"Client {sid} left artwork {artwork_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
