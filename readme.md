# API Endpoints Documentation

## Admin Endpoints

### Create API Key
```bash
curl -X POST http://127.0.0.1:8000/admin/create_api_key \
  -F "admin_access=your-admin-access-key"
```
Response:
```json
{
  "api_key": "generated-api-key"
}
```

### Delete API Key
```bash
curl -X POST http://127.0.0.1:8000/admin/delete_api_key \
  -F "admin_access=your-admin-access-key" \
  -F "api_key_to_delete=key-to-delete"
```
Response:
```json
{
  "detail": "API key deleted"
}
```

## Project Endpoints

### Get Available Voices
```bash
curl -X GET http://127.0.0.1:8000/voices
```
Response:
```json
{
  "voices": [
    ["en-US-EricNeural", "American English - Male (Eric)"]
  ]
}
```

### Create Project with Text
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: 3329ad25f0af871903c31411dccc5fe3" \
  -F "voice=en-US-EricNeural" \
  -F "text=Hello, this is a test."
```
Response:
```json
{
  "uuid": "project-uuid",
  "status": "processing"
}
```

### Create Project with Text File
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: your-api-key" \
  -F "voice=en-US-EricNeural" \
  -F "file=@/path/to/your/file.txt"
```
Response:
```json
{
  "uuid": "project-uuid",
  "status": "processing"
}
```

### Check Project Status
```bash
curl -X GET http://127.0.0.1:8000/projects/{uuid}/status \
  -H "api_key: your-api-key"
```
Response:
```json
{
  "uuid": "project-uuid",
  "status": "completed"  # or "processing", "failed"
}
```

### Get Project Download URL
```bash
curl -X GET http://127.0.0.1:8000/projects/{uuid}/download \
  -H "api_key: your-api-key"
```
Response:
```json
{
  "download_url": "https://..."
}
```

### Delete Project
```bash
curl -X DELETE http://127.0.0.1:8000/projects/{uuid} \
  -H "api_key: your-api-key"
```
Response:
```json
{
  "detail": "Project deleted"
}
```

## Example Workflow

1. First, create an API key:
```bash
curl -X POST http://127.0.0.1:8000/admin/create_api_key \
  -F "admin_access=your-admin-access-key"
```

2. Create a new project with some text:
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "api_key: your-new-api-key" \
  -F "voice=en-US-EricNeural" \
  -F "text=Hello, this is a test of the text to speech system."
```

3. Check the project status using the UUID from step 2:
```bash
curl -X GET http://127.0.0.1:8000/projects/your-uuid/status \
  -H "api_key: your-new-api-key"
```

4. Once status is "completed", get the download URL:
```bash
curl -X GET http://127.0.0.1:8000/projects/your-uuid/download \
  -H "api_key: your-new-api-key"
```

5. Download the file using the URL from the response:
```bash
curl -o output.mp3 "download-url-from-response"
```

Note: Replace placeholders like:
- `your-admin-access-key` with your actual admin access key
- `your-api-key` with the API key you received
- `your-uuid` with the actual UUID received from create project
- `project-uuid` with actual project UUID