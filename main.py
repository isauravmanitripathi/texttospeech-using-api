from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Response, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
from sqlalchemy.orm import Session
import models, crud, utils
from database import SessionLocal, engine
from fastapi.security import APIKeyHeader
from typing import Optional
import os
import uuid
import asyncio
import edge_tts
import datetime
import logging
import b2sdk.v2 as b2
from starlette.responses import RedirectResponse
from dotenv import load_dotenv 
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Get the directory containing your script
BASE_DIR = Path(__file__).resolve().parent

# Load .env file with explicit path
load_dotenv(BASE_DIR / '.env')

# Debug logging for environment variables
logger.debug("------------ Environment Variables Debug ------------")
logger.debug(f"ADMIN_ACCESS from env: {os.getenv('ADMIN_ACCESS')}")
logger.debug(f"Current directory: {os.getcwd()}")
logger.debug(f"Looking for .env file at: {BASE_DIR / '.env'}")
logger.debug(f"Does .env file exist? {(BASE_DIR / '.env').exists()}")
logger.debug("--------------------------------------------------")

# Read from environment variables
ADMIN_ACCESS = os.getenv("ADMIN_ACCESS")
B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

API_KEY_NAME = "api_key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# List of available voices
voices = [
    ("en-US-EricNeural", "American English - Male (Eric)"),
    ("en-US-ChristopherNeural", "American English - Male (Christopher)"),
    ("en-US-GuyNeural", "American Guy Multiple Speech"),
    ("en-GB-ThomasNeural", "British English - Male (Thomas)"),
    ("en-IN-PrabhatNeural", "Indian English - Male (Prabhat)"),
    ("en-IN-NeerjaNeural", "Indian English - Female (Neerja)"),
    ("hi-IN-MadhurNeural", "Hindi - Male (Madhur)"),
    ("hi-IN-SwaraNeural", "Hindi - Female (Swara)"),
    ("bn-IN-BashkarNeural", "Bengali - Male (Bashkar)"),
    ("bn-IN-TanishaaNeural", "Bengali - Female (Tanishaa)"),
    ("gu-IN-NiranjanNeural", "Gujarati - Male (Niranjan)"),
    ("gu-IN-DhwaniNeural", "Gujarati - Female (Dhwani)"),
    ("ta-IN-ValluvarNeural", "Tamil - Male (Valluvar)"),
    ("ta-IN-PallaviNeural", "Tamil - Female (Pallavi)"),
    ("te-IN-MohanNeural", "Telugu - Male (Mohan)"),
    ("te-IN-ShrutiNeural", "Telugu - Female (Shruti)"),
    ("es-ES-AlvaroNeural", "Spanish (Spain) - Male (Alvaro)"),
    ("fr-FR-HenriNeural", "French - Male (Henri)"),
    ("de-DE-KillianNeural", "German - Male (Killian)"),
    ("zh-CN-YunxiNeural", "Chinese (Mandarin) - Male (Yunxi)"),
    ("en-US-JennyNeural", "American English - Female (Jenny)")
]

# Create voice map
voice_map = {voice[0]: voice[1] for voice in voices}

async def text_to_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_bytes = b""
    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        raise

def get_current_user(api_key: str = Depends(api_key_header), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key missing")
    user = crud.get_user_by_api_key(db, api_key=api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

@app.get("/voices")
def get_voices():
    return JSONResponse(content={"voices": voices})

@app.post("/admin/create_api_key")
def create_api_key(admin_access: str = Form(...), db: Session = Depends(get_db)):
    logger.debug(f"Received admin_access: {admin_access}")
    logger.debug(f"Expected admin_access: {ADMIN_ACCESS}")
    logger.debug(f"Type of received: {type(admin_access)}")
    logger.debug(f"Type of expected: {type(ADMIN_ACCESS)}")
    
    if admin_access != ADMIN_ACCESS:
        logger.debug("Access keys don't match!")
        raise HTTPException(status_code=403, detail="Invalid admin access key")
    new_api_key = utils.generate_api_key()
    user = crud.create_user(db, api_key=new_api_key)
    return {"api_key": new_api_key}

@app.post("/admin/delete_api_key")
def delete_api_key(admin_access: str = Form(...), api_key_to_delete: str = Form(...), db: Session = Depends(get_db)):
    if admin_access != ADMIN_ACCESS:
        raise HTTPException(status_code=403, detail="Invalid admin access key")
    success = crud.delete_user(db, api_key=api_key_to_delete)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"detail": "API key deleted"}

@app.post("/projects/")
async def create_project(voice: str = Form(...), file: UploadFile = File(None), text: str = Form(None), 
                         current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if voice not in voice_map:
        raise HTTPException(status_code=400, detail="Invalid voice selection")

    if text is None and file is None:
        raise HTTPException(status_code=400, detail="Either text or file must be provided")

    original_filename = None
    text_content = None
    if file:
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are allowed")
        original_filename = file.filename
        text_content = (await file.read()).decode('utf-8')
    else:
        original_filename = "input.txt"
        text_content = text

    project = crud.create_project(
        db,
        user_id=current_user.id,
        voice=voice,
        text=text_content,
        original_filename=original_filename
    )

    # Start background processing
    asyncio.create_task(process_project(project.id))

    return {"uuid": project.uuid, "status": project.status}

@app.get("/projects/{uuid}/status")
def check_project_status(uuid: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = crud.get_project_by_uuid(db, uuid=uuid)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "uuid": project.uuid,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "voice": project.voice,
        "original_filename": project.original_filename
    }

@app.get("/projects/{uuid}/url")
def get_project_url(uuid: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = crud.get_project_by_uuid(db, uuid=uuid)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not completed yet")
    if not project.b2_audio_download_url:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return {
        "audio_url": project.b2_audio_download_url,
        "text_url": project.b2_txt_download_url
    }

@app.get("/projects/{uuid}/download")
async def download_audio(uuid: str, direct: bool = False, current_user: models.User = Depends(get_current_user), 
                         db: Session = Depends(get_db)):
    project = crud.get_project_by_uuid(db, uuid=uuid)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not completed yet")
    if not project.b2_audio_download_url:
        raise HTTPException(status_code=404, detail="Audio file not found")

    if direct:
        # Direct download through server
        async with httpx.AsyncClient() as client:
            response = await client.get(project.b2_audio_download_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download file")
            
            filename = f"{project.original_filename}_{project.uuid}.mp3"
            return Response(
                content=response.content,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
    else:
        # Redirect to the download URL
        return RedirectResponse(url=project.b2_audio_download_url)

@app.get("/projects/{uuid}/download/text")
async def download_text(uuid: str, direct: bool = False, current_user: models.User = Depends(get_current_user), 
                        db: Session = Depends(get_db)):
    project = crud.get_project_by_uuid(db, uuid=uuid)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not completed yet")
    if not project.b2_txt_download_url:
        raise HTTPException(status_code=404, detail="Text file not found")

    if direct:
        # Direct download through server
        async with httpx.AsyncClient() as client:
            response = await client.get(project.b2_txt_download_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download file")
            
            filename = f"{project.original_filename}_{project.uuid}.txt"
            return Response(
                content=response.content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
    else:
        # Redirect to the download URL
        return RedirectResponse(url=project.b2_txt_download_url)

@app.delete("/projects/{uuid}")
def delete_project(uuid: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = crud.get_project_by_uuid(db, uuid=uuid)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # Authorize with Backblaze B2 and get bucket
    try:
        info = b2.InMemoryAccountInfo()
        b2_api = b2.B2Api(info)
        key_id = f"00{B2_KEY_ID}" if not B2_KEY_ID.startswith('00') else B2_KEY_ID
        b2_api.authorize_account("production", key_id, B2_APPLICATION_KEY)
        b2_bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
    except b2.exception.B2Error as e:
        logger.error(f"B2 authorization failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to authorize with Backblaze B2.")

    # Delete files from Backblaze B2
    if project.b2_audio_file_key:
        try:
            file_versions = b2_bucket.ls(file_name=project.b2_audio_file_key, recursive=True)
            for file_version, _ in file_versions:
                b2_bucket.delete_file_version(file_version.id_, file_version.file_name)
            logger.info(f"Deleted audio file from B2: {project.b2_audio_file_key}")
        except Exception as e:
            logger.error(f"Failed to delete audio file from B2: {e}")

    if project.b2_txt_file_key:
        try:
            file_versions = b2_bucket.ls(file_name=project.b2_txt_file_key, recursive=True)
            for file_version, _ in file_versions:
                b2_bucket.delete_file_version(file_version.id_, file_version.file_name)
            logger.info(f"Deleted text file from B2: {project.b2_txt_file_key}")
        except Exception as e:
            logger.error(f"Failed to delete text file from B2: {e}")

    # Delete project from DB
    success = crud.delete_project(db, project_id=project.id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete project")
    return {"detail": "Project deleted"}

@app.post("/admin/reset_database")
def reset_database(admin_access: str = Form(...)):
    if admin_access != ADMIN_ACCESS:
        raise HTTPException(status_code=403, detail="Invalid admin access key")

    db_path = "sqlite3.db"  # Specify the path to your SQLite database file here

    # Delete the database file
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Database file deleted successfully.")
    else:
        raise HTTPException(status_code=404, detail="Database file not found")

    # Recreate the tables
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database recreated successfully.")

    return {"detail": "Database reset successfully"}

async def process_project(project_id: int):
    db = SessionLocal()
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            logger.error(f"Project with ID {project_id} not found.")
            return

        logger.info(f"Starting processing for project {project.uuid}")

        unique_id = project.uuid
        original_name = project.original_filename
        base_name = os.path.splitext(original_name)[0]

        # Format today's date as a folder name
        date_folder = datetime.datetime.now().strftime('%Y-%m-%d')

        txt_filename = f"{base_name}_{unique_id}.txt"
        mp3_filename = f"{base_name}_{unique_id}.mp3"

        # Paths in B2 bucket
        txt_key = f"{date_folder}/{txt_filename}"
        mp3_key = f"{date_folder}/{mp3_filename}"

        # Perform text-to-speech
        try:
            logger.info(f"Converting text to speech for project {project.uuid}")
            audio_bytes = await text_to_speech(project.text, project.voice)
        except Exception as e:
            project.status = "failed"
            logger.error(f"Failed to convert text to speech for project {project.uuid}: {e}")
            db.commit()
            return

        # Authorize with Backblaze B2 and get bucket
        try:
            info = b2.InMemoryAccountInfo()
            b2_api = b2.B2Api(info)
            key_id = f"00{B2_KEY_ID}" if not B2_KEY_ID.startswith('00') else B2_KEY_ID
            b2_api.authorize_account("production", key_id, B2_APPLICATION_KEY)
            b2_bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        except b2.exception.B2Error as e:
            project.status = "failed"
            logger.error(f"B2 authorization failed: {e}")
            db.commit()
            return

        # Upload the text content to Backblaze B2
        try:
            logger.info(f"Uploading text file to B2: {txt_key}")
            txt_bytes = project.text.encode('utf-8')
            uploaded_txt = b2_bucket.upload_bytes(
                data_bytes=txt_bytes,
                file_name=txt_key,
                content_type='text/plain'
            )
            project.b2_txt_file_key = txt_key

            # Generate download URL
            txt_download_url = b2_bucket.get_download_url(txt_key)
            project.b2_txt_download_url = txt_download_url
            
            logger.info(f"Text file uploaded successfully: {txt_download_url}")
        except Exception as e:
            project.status = "failed"
            logger.error(f"Failed to upload text file to B2: {e}")
            db.commit()
            return

        # Upload the audio file to Backblaze B2
        try:
            logger.info(f"Uploading audio file to B2: {mp3_key}")
            uploaded_audio = b2_bucket.upload_bytes(
                data_bytes=audio_bytes,
                file_name=mp3_key,
                content_type='audio/mpeg'
            )
            project.b2_audio_file_key = mp3_key

            # Generate download URL
            audio_download_url = b2_bucket.get_download_url(mp3_key)
            project.b2_audio_download_url = audio_download_url
            
            logger.info(f"Audio file uploaded successfully: {audio_download_url}")

            project.status = "completed"
        except Exception as e:
            project.status = "failed"
            logger.error(f"Failed to upload audio file to B2: {e}")
        finally:
            project.updated_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(project)
            logger.info(f"Finished processing project {project.uuid} with status {project.status}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
