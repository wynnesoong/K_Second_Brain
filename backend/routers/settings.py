from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.services.settings_service import SettingsService, SystemSettings

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsResponse(BaseModel):
    ai_provider: str
    ai_model_list: List[str]
    # Allow loose dict for other keys to support masking
    model_config = {"extra": "allow"}

class UpdateSettingsRequest(BaseModel):
    ai_provider: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    moonshot_api_key: Optional[str] = None
    dashscope_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None
    
    notebooklm_source_folder_id: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    slack_app_token: Optional[str] = None

@router.get("/", response_model=Dict[str, Any])
async def get_settings():
    """
    取得系統設定 (敏感資訊已遮罩)
    """
    service = SettingsService()
    return service.get_masked_settings()

@router.post("/", response_model=Dict[str, Any])
async def update_settings(request: UpdateSettingsRequest):
    """
    更新系統設定
    """
    service = SettingsService()
    try:
        # Convert Pydantic model to dict, excluding None values
        new_settings = request.model_dump(exclude_unset=True)
        service.update_settings(new_settings)
        return {"status": "success", "message": "Settings updated and synced to .env"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
