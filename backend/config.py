from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    第二大腦設定檔
    支援 10 種 AI 模型以及 NotebookLM, Slack, Obsidian 整合設定。
    """
    # 應用程式設定
    app_name: str = "Kevin Second Brain"
    app_version: str = "1.5.0"
    debug: bool = False

    # AI Provider (10 Models Support)
    # 可選值: gemini, openai, ollama, claude, deepseek, mistral, groq, openrouter, kimi, qwen
    ai_provider: str = Field(default="gemini", env="AI_PROVIDER")
    
    # AI API Keys
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    moonshot_api_key: Optional[str] = None  # Kimi
    dashscope_api_key: Optional[str] = None # Qwen (可選，或使用 openai_api_key 兼容)

    # Google Drive (NotebookLM 同步)
    # 若在 Docker 內，預設路徑為 /app/credentials.json
    google_application_credentials: str = "/app/credentials.json"
    notebooklm_source_folder_id: Optional[str] = None

    # Slack 整合
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    slack_app_token: Optional[str] = None

    # Obsidian 設定
    obsidian_vault_path: str = "/obsidian_vault"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # 忽略多餘變數
    )

settings = Settings()
