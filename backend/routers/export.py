from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.export import ExportResponse
from backend.services.drive_exporter import DriveExporter
from backend.config import settings
import os

router = APIRouter(prefix="/export", tags=["Export"])

@router.post("/drive/{filename}", response_model=ExportResponse)
async def export_to_drive(filename: str):
    """
    將指定筆記同步至 Google Drive (NotebookLM)
    """
    exporter = DriveExporter()
    file_path = os.path.join(settings.obsidian_vault_path, "notes", filename)
    
    if not os.path.exists(file_path):
        # Check inbox
        file_path = os.path.join(settings.obsidian_vault_path, "inbox", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Note not found")

    try:
        drive_file_id = await exporter.upload_file(file_path, filename)
        return ExportResponse(status="success", drive_file_id=drive_file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
