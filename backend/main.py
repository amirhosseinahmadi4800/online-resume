from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from . import models, schemas
from .database import SessionLocal, engine
from .auth import authenticate_user, create_access_token, get_current_admin


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Project API")
active_connections = set()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(data: schemas.LoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/admin/requests", response_model=list[schemas.ProjectRequestResponse])
def get_requests(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    return db.query(models.ProjectRequest).all()


@app.delete("/admin/requests/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    req = db.query(models.ProjectRequest).get(request_id)
    if not req:
        raise HTTPException(status_code=404)
    db.delete(req)
    db.commit()
    return {"message": "Deleted"}


@app.put("/admin/requests/{request_id}/status")
def update_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    req = db.query(models.ProjectRequest).get(request_id)
    if not req:
        raise HTTPException(status_code=404)
    req.status = status
    db.commit()
    return {"message": "Updated"}


@app.post("/requests", response_model=schemas.ProjectRequestResponse)
def create_request(
    request: schemas.ProjectRequestCreate,
    db: Session = Depends(get_db)
):
    db_request = models.ProjectRequest(**request.dict())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


@app.websocket("/ws/online")
async def websocket_online(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)

    try:
        while True:
            count = len(active_connections)
            for conn in active_connections:
                await conn.send_text(str(count))
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        count = len(active_connections)
        for conn in active_connections:
            await conn.send_text(str(count))
