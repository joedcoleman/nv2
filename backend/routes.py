from typing import List
import toml
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services import process_message
from database import get_db
import schemas
import services

router = APIRouter()

connected_websockets: List[WebSocket] = []

config = toml.load("../settings.toml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        try:
            message = await websocket.receive_json()
            async for chunk in process_message(db, message):
                await websocket.send_json(chunk)

        except Exception as e:
            print(f"Error: {e}")
            break


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
    return config


@router.post("/auth")
def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # Very simple auth check..
    if username != config["auth"]["username"] or password != config["auth"]["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return {"token": config["auth"]["token"]}
