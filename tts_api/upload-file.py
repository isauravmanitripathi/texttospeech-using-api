from datetime import datetime
import os
import b2sdk.v2 as b2

def upload_file_to_b2(bucket_name):
    # Initialize B2 API
    info = b2.InMemoryAccountInfo()
    b2_api = b2.B2Api(info)
    
    # Authorization with your new credentials
    application_key_id = '00535159b90450c0000000002'
    application_key = 'K005BwP+pVbP7raXAvLNMYNhQ8iLTYM'
    b2_api.authorize_account("production", application_key_id, application_key)
    
    try:
        # Get bucket object
        bucket = b2_api.get_bucket_by_name(bucket_name)
        
        # Prompt for the file path
        local_path = input("Please enter the path to the file you want to upload: ")
        
        # Ensure file exists
        if not os.path.exists(local_path):
            print(f"Error: File {local_path} does not exist")
            return
        
        # Format today's date as a folder name
        date_folder = datetime.now().strftime('%Y-%m-%d')
        base_name = os.path.basename(local_path)
        b2_key = f"{date_folder}/{base_name}"
        
        print(f"Uploading {local_path} to {bucket_name}/{b2_key}")
        
        # Upload file - Fixed this part
        uploaded_file = bucket.upload_local_file(
            local_file=local_path,  # Changed this line - now passing the path directly
            file_name=b2_key
        )
        
        # Generate download URL
        download_url = f"https://s3.us-east-005.backblazeb2.com/{bucket_name}/{b2_key}"
        
        print(f"Upload complete!")
        print(f"File ID: {uploaded_file.id_}")
        print(f"File can be downloaded from: {download_url}")
        
    except b2.exception.B2Error as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    BUCKET_NAME = "audio-files-apative-pitch"
    upload_file_to_b2(BUCKET_NAME)