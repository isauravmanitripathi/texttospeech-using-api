# Text-to-Speech API with Backblaze Storage

## Overview
This program is a FastAPI-based web service that converts text to speech using Microsoft Edge's TTS engine and stores both the text and audio files in Backblaze B2 cloud storage. It supports user authentication via API keys and provides various endpoints for managing text-to-speech conversions.

## Features
- Text to Speech conversion
- File upload support (txt files)
- Secure storage in Backblaze B2
- API key authentication
- Date-based file organization
- Direct and redirect download options
- Project status tracking

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

```bash
aiofiles==24.1.0
aiohappyeyeballs==2.4.3
aiohttp==3.10.10
aiosignal==1.3.1
annotated-types==0.7.0
anyio==4.6.2.post1
attrs==24.2.0
b2sdk==2.6.0
boto3==1.35.54
botocore==1.35.54
certifi==2024.8.30
charset-normalizer==3.4.0
click==8.1.7
edge-tts==6.1.15
fastapi==0.115.4
frozenlist==1.5.0
h11==0.14.0
httpcore==1.0.6
httpx==0.27.2
idna==3.10
jmespath==1.0.1
logfury==1.0.1
multidict==6.1.0
propcache==0.2.0
pydantic==2.9.2
pydantic_core==2.23.4
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
python-multipart==0.0.17
requests==2.32.3
s3transfer==0.10.3
six==1.16.0
sniffio==1.3.1
SQLAlchemy==2.0.36
starlette==0.41.2
typing_extensions==4.12.2
urllib3==2.2.3
uvicorn==0.32.0
yarl==1.17.1
```

### 2. Environment Configuration
Create a `.env` file in your project root with the following content:
```env
ADMIN_ACCESS=your_admin_access_key
B2_KEY_ID=your_backblaze_key_id
B2_APPLICATION_KEY=your_backblaze_application_key
B2_BUCKET_NAME=your_bucket_name
```

### 3. Reset Database
To start fresh:
1. Stop the server if it's running
2. Delete the existing database:
```bash
rm sql_app.db  # Or whatever your database filename is
```
3. Restart the server - it will create a new database automatically:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Admin Endpoints

#### 1. Create API Key (Admin Only)

Generates a new API key for a user.

```bash
curl -X POST "http://127.0.0.1:8000/admin/create_api_key" \
    -F "admin_access=<ADMIN_ACCESS>"
```

- **Method**: `POST`
- **URL**: `/admin/create_api_key`
- **Form Data**:
  - `admin_access`: Your admin access key.
- **Response**:
  - `api_key`: The newly generated API key.

#### 2. Delete API Key (Admin Only)

Deletes an existing API key.

```bash
curl -X POST "http://127.0.0.1:8000/admin/delete_api_key" \
    -F "admin_access=<ADMIN_ACCESS>" \
    -F "api_key_to_delete=<API_KEY_TO_DELETE>"
```

- **Method**: `POST`
- **URL**: `/admin/delete_api_key`
- **Form Data**:
  - `admin_access`: Your admin access key.
  - `api_key_to_delete`: The API key you want to delete.
- **Response**:
  - `detail`: Confirmation message.

#### 3. Reset Database (Admin Only)

Deletes the existing database and recreates it.

```bash
curl -X POST "http://127.0.0.1:8000/admin/reset_database" \
    -F "admin_access=<ADMIN_ACCESS>"
```

- **Method**: `POST`
- **URL**: `/admin/reset_database`
- **Form Data**:
  - `admin_access`: Your admin access key.
- **Response**:
  - `detail`: Confirmation message.

### User Endpoints

#### 1. Get Available Voices

Retrieves the list of available voices for text-to-speech conversion.

```bash
curl -X GET "http://127.0.0.1:8000/voices"
```

- **Method**: `GET`
- **URL**: `/voices`
- **Response**:
  - `voices`: An array of available voices.

#### 2. Create a New Project

Creates a new text-to-speech project using either text input or a `.txt` file.

**Using Text Input**:

```bash
curl -X POST "http://127.0.0.1:8000/projects/" \
    -F "voice=en-US-JennyNeural" \
    -F "text=Hello, this is a test with Jenny's voice." \
    -H "api_key: <API_KEY>"
```

**Using a File**:

```bash
curl -X POST "http://127.0.0.1:8000/projects/" \
    -F "voice=en-US-JennyNeural" \
    -F "file=@/path/to/yourfile.txt" \
    -H "api_key: <API_KEY>"
```

- **Method**: `POST`
- **URL**: `/projects/`
- **Headers**:
  - `api_key`: Your API key.
- **Form Data**:
  - `voice`: The voice to use for conversion.
  - `text`: The text to convert (if not using a file).
  - `file`: A `.txt` file containing the text to convert (if not using `text`).
- **Response**:
  - `uuid`: The unique identifier for the project.
  - `status`: The current status of the project.

#### 3. View the Queue

Retrieves the list of your projects currently in the queue.

```bash
curl -X GET "http://127.0.0.1:8000/queue" \
    -H "api_key: <API_KEY>"
```

- **Method**: `GET`
- **URL**: `/queue`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `queue`: An array of project UUIDs in your queue.

#### 4. Delete a Project from the Queue

Removes a specific project from the queue using its UUID.

```bash
curl -X DELETE "http://127.0.0.1:8000/queue/<PROJECT_UUID>" \
    -H "api_key: <API_KEY>"
```

- **Method**: `DELETE`
- **URL**: `/queue/<PROJECT_UUID>`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `detail`: Confirmation message.

#### 5. Move a Project to the Top of the Queue

Moves a specific project to the front of the queue.

```bash
curl -X POST "http://127.0.0.1:8000/queue/<PROJECT_UUID>/move_to_top" \
    -H "api_key: <API_KEY>"
```

- **Method**: `POST`
- **URL**: `/queue/<PROJECT_UUID>/move_to_top`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `detail`: Confirmation message.

#### 6. Check Project Status

Checks the status of a project by its UUID.

```bash
curl -X GET "http://127.0.0.1:8000/projects/<PROJECT_UUID>/status" \
    -H "api_key: <API_KEY>"
```

- **Method**: `GET`
- **URL**: `/projects/<PROJECT_UUID>/status`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `uuid`: Project UUID.
  - `status`: Current status (`queued`, `processing`, `completed`, etc.).
  - `created_at`: Creation timestamp.
  - `updated_at`: Last update timestamp.
  - `voice`: Voice used.
  - `original_filename`: Original filename if a file was used.

#### 7. Get Project URL

Retrieves the download URLs for the audio and text files if the project is completed.

```bash
curl -X GET "http://127.0.0.1:8000/projects/<PROJECT_UUID>/url" \
    -H "api_key: <API_KEY>"
```

- **Method**: `GET`
- **URL**: `/projects/<PROJECT_UUID>/url`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `audio_url`: URL to download the audio file.
  - `text_url`: URL to download the text file.

#### 8. Download Project Audio

Downloads the audio file for the project. If you want to download directly through the server, set `direct=true`.

```bash
curl -X GET "http://127.0.0.1:8000/projects/<PROJECT_UUID>/download?direct=true" \
    -H "api_key: <API_KEY>" -o "output.mp3"
```

- **Method**: `GET`
- **URL**: `/projects/<PROJECT_UUID>/download`
- **Headers**:
  - `api_key`: Your API key.
- **Query Parameters**:
  - `direct`: Set to `true` to download directly through the server.
- **Response**:
  - Returns the audio file.

#### 9. Download Project Text File

Downloads the text file for the project. Set `direct=true` to download directly through the server.

```bash
curl -X GET "http://127.0.0.1:8000/projects/<PROJECT_UUID>/download/text?direct=true" \
    -H "api_key: <API_KEY>" -o "output.txt"
```

- **Method**: `GET`
- **URL**: `/projects/<PROJECT_UUID>/download/text`
- **Headers**:
  - `api_key`: Your API key.
- **Query Parameters**:
  - `direct`: Set to `true` to download directly through the server.
- **Response**:
  - Returns the text file.

#### 10. Delete a Project

Deletes an existing project by its UUID.

```bash
curl -X DELETE "http://127.0.0.1:8000/projects/<PROJECT_UUID>" \
    -H "api_key: <API_KEY>"
```

- **Method**: `DELETE`
- **URL**: `/projects/<PROJECT_UUID>`
- **Headers**:
  - `api_key`: Your API key.
- **Response**:
  - `detail`: Confirmation message.

---

## Notes

- **Placeholders**: Replace placeholders like `<ADMIN_ACCESS>`, `<API_KEY>`, `<PROJECT_UUID>`, and `/path/to/yourfile.txt` with actual values.
- **API Key**: You must include your API key in the header for endpoints that require authentication.
- **Admin Access**: Admin endpoints require the `admin_access` key, which is defined in your `.env` file.
- **Queue Limit**: The processing queue has a maximum limit of 15 projects. If the queue is full, new projects will be rejected.
- **Project Statuses**:
  - `queued`: Project is waiting in the queue.
  - `processing`: Project is currently being processed.
  - `completed`: Project has been processed successfully.
  - `failed`: An error occurred during processing.
  - `deleted`: Project was removed from the queue before processing.
  - `rejected`: Project was rejected due to the queue being full.

---

## Examples

### Creating a Project with Text Input

```bash
curl -X POST "http://127.0.0.1:8000/projects/" \
    -F "voice=en-US-EricNeural" \
    -F "text=This is a sample text for conversion." \
    -H "api_key: your_api_key_here"
```

### Creating a Project with a File

```bash
curl -X POST "http://127.0.0.1:8000/projects/" \
    -F "voice=en-US-EricNeural" \
    -F "file=@/Users/username/Documents/sample.txt" \
    -H "api_key: your_api_key_here"
```


## Working with Environment Variables

### Updating Your Keys
1. Stop the server
2. Edit your `.env` file with new values:
```env
# Admin access key for creating API keys
ADMIN_ACCESS=your_new_admin_key

# Backblaze B2 credentials
B2_KEY_ID=your_new_b2_key_id
B2_APPLICATION_KEY=your_new_b2_application_key
B2_BUCKET_NAME=your_new_bucket_name
```
3. Restart the server

### Getting Backblaze Credentials
1. Log into your Backblaze account
2. Go to App Keys or Account > App Keys
3. Create a new application key
4. Note down:
   - Application Key ID (B2_KEY_ID)
   - Application Key (B2_APPLICATION_KEY)
   - Bucket name (B2_BUCKET_NAME)

## Database Management

### Reset Database
If you need to start fresh:
```bash
# Stop the server
ctrl+c

# Delete the database
rm sql_app.db

# Restart the server (creates new database)
uvicorn main:app --reload
```

### Database Location
- The default SQLite database is created as `sql_app.db` in your project directory
- A new database is automatically created if it doesn't exist when you start the server

## Common Operations

### Complete Reset
To completely reset your application:
1. Stop the server
2. Delete the database: `rm sql_app.db`
3. Update `.env` file if needed
4. Restart server: `uvicorn main:app --reload`
5. Create new API key using admin access
6. Start using new API key for operations

### Testing Setup
1. Create API key:
```bash
curl -X POST http://127.0.0.1:8000/admin/create_api_key \
  -F "admin_access=your_admin_access_key"
```
2. Test voices endpoint:
```bash
curl -X GET http://127.0.0.1:8000/voices
```
3. Create test project:
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: your_new_api_key" \
  -F "voice=en-US-EricNeural" \
  -F "text=This is a test of the text to speech system."
```

## Error Handling
- Missing API key: 400 Bad Request
- Invalid API key: 401 Unauthorized
- Invalid admin access: 403 Forbidden
- Project not found: 404 Not Found
- Upload/download failures: 500 Internal Server Error

## Security Notes
- Keep your `.env` file secure and never commit it to version control
- Regularly rotate your API keys
- Use HTTPS in production
- Monitor your Backblaze usage and costs