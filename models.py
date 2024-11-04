from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
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
    b2_audio_download_url = Column(String)  # New field
    b2_txt_download_url = Column(String)    # New field

    owner = relationship("User", back_populates="projects")
