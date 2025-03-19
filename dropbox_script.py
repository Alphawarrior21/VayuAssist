import dropbox
import os
from dotenv import load_dotenv


def download_files():
    # Load environment variables from .env file
    load_dotenv()
    
    local_path = os.getenv('DROPBOX_LOCAL_FOLDER_PATH')
    cloud_path = os.getenv('DROPBOX_CLOUD_FOLDER_PATH')
    
    if not local_path:
        raise ValueError("DROPBOX_LOCALFOLDERPATH is not set in the .env file")
    
    if not cloud_path:
        raise ValueError("DROPBOX_CLOUD_FOLDER_PATH is not set in the .env file")
    
       
    # Define your access token (consider using an env variable instead of hardcoding)
    ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')  # Store this securely in .env

    if not ACCESS_TOKEN:
        raise ValueError("Dropbox access token is not set in the .env file")

    # Initialize Dropbox object
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    # Specify the Dropbox path and local folder path
    # dropbox_path = '/RagBasedLLM'
    
    # Create local folder if it doesn't exist
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # List files in the Dropbox folder
    for entry in dbx.files_list_folder(cloud_path).entries:
        local_file_path = os.path.join(local_path, entry.name)
        # Check if the file already exists locally
        if not os.path.exists(local_file_path):
            # Download each file if it does not exist locally
            _, res = dbx.files_download(cloud_path + '/' + entry.name)
            data = res.content

            # Write the downloaded file to the local folder
            with open(local_file_path, 'wb') as f:
                f.write(data)
            print(f"Downloaded: {entry.name}")
        else:
            print(f"Skipped (already exists): {entry.name}")

    print("File check and download completed!")

#download_files()