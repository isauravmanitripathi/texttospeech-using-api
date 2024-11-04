# models.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base  # Corrected import
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    voice = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    original_filename = Column(String)
    b2_audio_file_key = Column(String)
    b2_txt_file_key = Column(String)
    b2_audio_download_url = Column(String)
    b2_txt_download_url = Column(String)

    owner = relationship("User", back_populates="projects")
    queue_entry = relationship("Queue", back_populates="project", uselist=False)

class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    position = Column(Integer, index=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="queue_entry")
