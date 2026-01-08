from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Project API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # بعداً می‌تونی محدودش کنی
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
