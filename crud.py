from sqlalchemy.orm import Session
import models
import uuid
import datetime

def get_user_by_api_key(db: Session, api_key: str):
    return db.query(models.User).filter(models.User.api_key == api_key).first()

def create_user(db: Session, api_key: str, is_admin: bool = False):
    db_user = models.User(api_key=api_key, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, api_key: str):
    db_user = get_user_by_api_key(db, api_key)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def create_project(db: Session, user_id: int, voice: str, text: str, original_filename: str):
    project_uuid = str(uuid.uuid4())
    db_project = models.Project(
        uuid=project_uuid,
        user_id=user_id,
        voice=voice,
        text=text,
        original_filename=original_filename,
        status="processing"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project_by_uuid(db: Session, uuid: str):
    return db.query(models.Project).filter(models.Project.uuid == uuid).first()

def update_project_status(db: Session, project_id: int, status: str, b2_audio_file_key: str = None):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db_project.status = status
        db_project.b2_audio_file_key = b2_audio_file_key
        db_project.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_project)
        return db_project
    return None

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False
