from pydantic import BaseModel
from typing import Optional
import datetime

class UserBase(BaseModel):
    api_key: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    voice: str
    text: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    uuid: str
    user_id: int
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    original_filename: str
    b2_audio_file_key: Optional[str]
    b2_txt_file_key: Optional[str]
    b2_audio_download_url: Optional[str]  # New field
    b2_txt_download_url: Optional[str]    # New field

    class Config:
        orm_mode = True
