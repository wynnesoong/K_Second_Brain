import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from backend.config import settings

class DriveExporter:
    def __init__(self):
        self.creds_path = settings.google_application_credentials
        self.folder_id = settings.notebooklm_source_folder_id
        self.service = None
        
        if os.path.exists(self.creds_path):
            creds = service_account.Credentials.from_service_account_file(
                self.creds_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=creds)
        else:
            print(f"Warning: Google Drive credentials not found at {self.creds_path}")

    async def upload_file(self, file_path: str, title: str) -> str:
        """
        上傳檔案到 Google Drive (轉換為 Google Doc 格式以供 NotebookLM 使用)
        """
        if not self.service:
            raise Exception("Google Drive Service not initialized")

        file_metadata = {
            'name': title,
            'parents': [self.folder_id] if self.folder_id else [],
            'mimeType': 'application/vnd.google-apps.document' # Convert to Google Doc
        }
        
        media = MediaFileUpload(file_path, mimetype='text/plain', resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            print(f"Drive Upload Error: {e}")
            raise e
