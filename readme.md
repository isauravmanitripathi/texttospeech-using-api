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

## API Usage

### 1. Admin Operations

#### Create API Key
```bash
curl -X POST http://127.0.0.1:8000/admin/create_api_key \
  -F "admin_access=your_admin_access_key"
```
Response:
```json
{
  "api_key": "generated_api_key"
}
```

#### Delete API Key
```bash
curl -X POST http://127.0.0.1:8000/admin/delete_api_key \
  -F "admin_access=your_admin_access_key" \
  -F "api_key_to_delete=key_to_delete"
```

### 2. Project Operations

#### List Available Voices
```bash
curl -X GET http://127.0.0.1:8000/voices
```

#### Create New Project (Text Input)
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: your_api_key" \
  -F "voice=en-US-EricNeural" \
  -F "text=Hello, this is a test."
```

#### Create New Project (File Input)
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: your_api_key" \
  -F "voice=en-US-EricNeural" \
  -F "file=@/path/to/your/file.txt"
```

#### Check Project Status
```bash
curl -X GET http://127.0.0.1:8000/projects/{uuid}/status \
  -H "api_key: your_api_key"
```

#### Get Project URLs
```bash
curl -X GET http://127.0.0.1:8000/projects/{uuid}/url \
  -H "api_key: your_api_key"
```

#### Download Audio File
```bash
# Direct download (through server)
curl -X GET "http://127.0.0.1:8000/projects/{uuid}/download?direct=true" \
  -H "api_key: your_api_key" \
  --output audio.mp3

# Redirect download (direct from Backblaze)
curl -X GET "http://127.0.0.1:8000/projects/{uuid}/download" \
  -H "api_key: your_api_key" \
  -L --output audio.mp3
```

#### Download Text File
```bash
# Direct download
curl -X GET "http://127.0.0.1:8000/projects/{uuid}/download/text?direct=true" \
  -H "api_key: your_api_key" \
  --output text.txt

# Redirect download
curl -X GET "http://127.0.0.1:8000/projects/{uuid}/download/text" \
  -H "api_key: your_api_key" \
  -L --output text.txt
```

#### Delete Project
```bash
curl -X DELETE http://127.0.0.1:8000/projects/{uuid} \
  -H "api_key: your_api_key"
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