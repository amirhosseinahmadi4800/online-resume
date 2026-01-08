from sqlalchemy import Column, Integer, String, Text
from database import Base

class ProjectRequest(Base):
    __tablename__ = "project_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    project_type = Column(String)
    budget = Column(String)
    description = Column(Text)
