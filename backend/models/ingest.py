from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class IngestUrlRequest(BaseModel):
    url: str

class IngestTextRequest(BaseModel):
    text: str
    source_url: Optional[str] = None  # 選填，例如 X 貼文網址

class IngestSalesforceRequest(BaseModel):
    message: str # Slack 轉發的原始訊息
    sender: Optional[str] = None # Slack user ID

class IngestResponse(BaseModel):
    status: str
    file_path: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
