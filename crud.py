# crud.py

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
        status="queued"
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

def add_project_to_queue(db: Session, project_id: int):
    max_queue_size = 15
    queue_count = db.query(models.Queue).count()
    if queue_count >= max_queue_size:
        return False  # Queue is full

    # Find the maximum position in the queue
    max_position_entry = db.query(models.Queue).order_by(models.Queue.position.desc()).first()
    next_position = (max_position_entry.position + 1) if max_position_entry else 1

    queue_entry = models.Queue(
        project_id=project_id,
        position=next_position
    )
    db.add(queue_entry)
    db.commit()
    return True

def remove_project_from_queue(db: Session, project_id: int):
    queue_entry = db.query(models.Queue).filter(models.Queue.project_id == project_id).first()
    if queue_entry:
        db.delete(queue_entry)
        db.commit()
        # Reorder positions
        reorder_queue_positions(db)
        return True
    return False

def move_project_to_top(db: Session, project_id: int):
    queue_entry = db.query(models.Queue).filter(models.Queue.project_id == project_id).first()
    if queue_entry:
        # Update positions of other entries
        db.query(models.Queue).filter(models.Queue.position < queue_entry.position).update({models.Queue.position: models.Queue.position + 1})
        queue_entry.position = 1
        db.commit()
        return True
    return False

def get_next_project_in_queue(db: Session):
    queue_entry = db.query(models.Queue).order_by(models.Queue.position).first()
    if queue_entry:
        return queue_entry.project_id
    return None

def get_user_queue(db: Session, user_id: int):
    queue_entries = db.query(models.Queue).join(models.Project).filter(models.Project.user_id == user_id).order_by(models.Queue.position).all()
    return [entry.project.uuid for entry in queue_entries]

def reorder_queue_positions(db: Session):
    queue_entries = db.query(models.Queue).order_by(models.Queue.position).all()
    for index, entry in enumerate(queue_entries, start=1):
        entry.position = index
    db.commit()
