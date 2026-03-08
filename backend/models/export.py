from pydantic import BaseModel

class ExportResponse(BaseModel):
    status: str
    drive_file_id: str
