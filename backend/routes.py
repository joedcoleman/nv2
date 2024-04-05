from typing import List
import toml
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import schemas
import services.services as services
from services.websocket_manager import websocket_manager

router = APIRouter()

connected_websockets: List[WebSocket] = []

config = toml.load("../settings.toml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            async for chunk in services.process_message(db, message):
                await websocket_manager.send_message(chunk)
    except Exception as e:
        pass


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conversation = services.get_conversation(conversation_id, db)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation


@router.get("/conversations", response_model=List[schemas.ConversationOut])
def get_conversations(db: Session = Depends(get_db)):
    return services.get_conversations(db=db)


@router.get("/settings", response_model=schemas.Settings)
def get_settings():
    return config["settings"]


@router.post("/auth")
def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if username != config["auth"]["username"] or password != config["auth"]["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return {"token": config["auth"]["token"]}
