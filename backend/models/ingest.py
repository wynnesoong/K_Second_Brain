from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class IngestUrlRequest(BaseModel):
    url: str

class IngestTextRequest(BaseModel):
    text: str

class IngestSalesforceRequest(BaseModel):
    message: str # Slack 轉發的原始訊息
    sender: Optional[str] = None # Slack user ID

class IngestResponse(BaseModel):
    status: str
    file_path: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
