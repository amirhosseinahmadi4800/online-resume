from pydantic import BaseModel

class ProjectRequestCreate(BaseModel):
    name: str
    email: str
    project_type: str | None = None
    budget: str | None = None
    description: str

class ProjectRequestResponse(ProjectRequestCreate):
    id: int

    class Config:
        orm_mode = True
