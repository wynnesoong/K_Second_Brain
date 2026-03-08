import os
from typing import Dict, Any, List
from backend.services.db import db
from backend.config import settings
from pydantic import BaseModel

class SystemSettings(BaseModel):
    # AI Config
    ai_provider: str
    
    # Keys (Optional if set in env, required if user wants to override)
    google_api_key: str | None = None
    openai_api_key: str | None = None
    moonshot_api_key: str | None = None
    dashscope_api_key: str | None = None
    anthropic_api_key: str | None = None
    deepseek_api_key: str | None = None
    mistral_api_key: str | None = None
    groq_api_key: str | None = None
    openrouter_api_key: str | None = None
    ollama_base_url: str = "http://host.docker.internal:11434"

    # Google Drive
    google_application_credentials: str = "/app/credentials.json"
    notebooklm_source_folder_id: str | None = None

    # Slack
    slack_bot_token: str | None = None
    slack_signing_secret: str | None = None
    slack_app_token: str | None = None

class SettingsService:
    def __init__(self):
        self.db = db

    def get_settings(self) -> Dict[str, Any]:
        """
        取得當前設定
        優先順序：DB > Env (Fallback)
        """
        db_settings = self.db.get_all_settings()
        
        # Merge Env Defaults
        config = {
            "ai_provider": db_settings.get("AI_PROVIDER") or settings.ai_provider,
            
            "google_api_key": db_settings.get("GOOGLE_API_KEY") or settings.google_api_key,
            "openai_api_key": db_settings.get("OPENAI_API_KEY") or settings.openai_api_key,
            "moonshot_api_key": db_settings.get("MOONSHOT_API_KEY") or settings.moonshot_api_key,
            "dashscope_api_key": db_settings.get("DASHSCOPE_API_KEY") or settings.dashscope_api_key,
            "anthropic_api_key": db_settings.get("ANTHROPIC_API_KEY") or settings.anthropic_api_key,
            "deepseek_api_key": db_settings.get("DEEPSEEK_API_KEY") or settings.deepseek_api_key,
            "mistral_api_key": db_settings.get("MISTRAL_API_KEY") or settings.mistral_api_key,
            "groq_api_key": db_settings.get("GROQ_API_KEY") or settings.groq_api_key,
            "openrouter_api_key": db_settings.get("OPENROUTER_API_KEY") or settings.openrouter_api_key,
            "ollama_base_url": db_settings.get("OLLAMA_BASE_URL") or settings.ollama_base_url,

            "google_application_credentials": db_settings.get("GOOGLE_APPLICATION_CREDENTIALS") or settings.google_application_credentials,
            "notebooklm_source_folder_id": db_settings.get("NOTEBOOKLM_SOURCE_FOLDER_ID") or settings.notebooklm_source_folder_id,
            
            "slack_bot_token": db_settings.get("SLACK_BOT_TOKEN") or settings.slack_bot_token,
            "slack_signing_secret": db_settings.get("SLACK_SIGNING_SECRET") or settings.slack_signing_secret,
            "slack_app_token": db_settings.get("SLACK_APP_TOKEN") or settings.slack_app_token,
        }
        
        return config
    
    def get_masked_settings(self) -> Dict[str, Any]:
        """
        取得遮罩後的設定 (Web UI 顯示用)
        """
        config = self.get_settings()
        masked = config.copy()
        
        for key in masked:
            val = masked[key]
            if val and "key" in key.lower() or "token" in key.lower() or "secret" in key.lower():
                if len(val) > 8:
                    masked[key] = val[:4] + "..." + val[-4:]
                else:
                    masked[key] = "***"
        
        # Add model list for UI dropdown
        masked["ai_model_list"] = [
            "gemini", "openai", "ollama", "claude", "deepseek", 
            "mistral", "groq", "openrouter", "kimi", "qwen"
        ]
        return masked

    def update_settings(self, new_settings: Dict[str, Any]):
        """
        更新設定至 DB 並同步 .env
        """
        # Save to DB
        for key, value in new_settings.items():
            if value is not None:
                # Store as uppercase keys to match Env conventions
                upper_key = key.upper()
                self.db.set_setting(upper_key, str(value))
        
        # Sync to .env file
        self._sync_to_env_file()
        
        # Reload Pydantic Settings? No need, ai_service calls get_settings() directly.
        pass

    def _sync_to_env_file(self):
        """
        將當前 DB 設定同步寫入 .env 檔案
        """
        current_config = self.get_settings()
        env_content = ""
        
        # Keys to persist
        keys_to_write = [
            "AI_PROVIDER",
            "GOOGLE_API_KEY", "OPENAI_API_KEY", "MOONSHOT_API_KEY", "DASHSCOPE_API_KEY",
            "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "MISTRAL_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
            "OLLAMA_BASE_URL",
            "GOOGLE_APPLICATION_CREDENTIALS", "NOTEBOOKLM_SOURCE_FOLDER_ID",
            "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN",
            "OBSIDIAN_VAULT_PATH"
        ]

        # Read existing .env to preserve comments if possible? 
        # For simplicity, we rewrite it. User said "System writes to env", implying overwrite.
        
        env_content += "# Auto-generated by Kevin Second Brain System\n"
        env_content += f"# Last Updated: {os.popen('date').read().strip()}\n\n"
        
        for key in keys_to_write:
            val = current_config.get(key.lower())
            if val:
                env_content += f"{key}={val}\n"
            else:
                env_content += f"{key}=\n"
                
        try:
            with open(".env", "w") as f:
                f.write(env_content)
        except Exception as e:
            print(f"Error writing to .env: {e}")
