from typing import Dict, Any, List
# from functools import lru_cache # Remove lru_cache for dynamic settings

from backend.services.settings_service import SettingsService # Use SettingsService
from backend.services.llm.base import LLMProvider
from backend.services.llm.gemini import GeminiProvider
from backend.services.llm.openai import OpenAIProvider
from backend.services.llm.ollama import OllamaProvider
from backend.services.llm.claude import ClaudeProvider
from backend.services.llm.deepseek import DeepSeekProvider
from backend.services.llm.mistral import MistralProvider
from backend.services.llm.groq import GroqProvider
from backend.services.llm.openrouter import OpenRouterProvider
from backend.services.llm.kimi import KimiProvider
from backend.services.llm.qwen import QwenProvider

def get_llm_provider() -> LLMProvider:
    """
    Factory Function: 根據 DB 設定回傳對應的 LLM Provider 實例。
    支援動態切換，不快取。
    """
    settings_service = SettingsService()
    config = settings_service.get_settings()
    
    provider_type = config.get("ai_provider", "gemini").lower()
    
    print(f"Initializing AI Provider: {provider_type}")
    
    try:
        if provider_type == "gemini":
            return GeminiProvider(api_key=config.get("google_api_key"))
        
        elif provider_type == "openai":
            return OpenAIProvider(api_key=config.get("openai_api_key"))
        
        elif provider_type == "ollama":
            return OllamaProvider(base_url=config.get("ollama_base_url"))
        
        elif provider_type == "claude":
            return ClaudeProvider(api_key=config.get("anthropic_api_key"))
        
        elif provider_type == "deepseek":
            return DeepSeekProvider(api_key=config.get("deepseek_api_key") or config.get("openai_api_key"))
        
        elif provider_type == "mistral":
            return MistralProvider(api_key=config.get("mistral_api_key") or config.get("openai_api_key"))
        
        elif provider_type == "groq":
            return GroqProvider(api_key=config.get("groq_api_key") or config.get("openai_api_key"))
        
        elif provider_type == "openrouter":
            return OpenRouterProvider(api_key=config.get("openrouter_api_key") or config.get("openai_api_key"))
        
        elif provider_type == "kimi":
            return KimiProvider(api_key=config.get("moonshot_api_key") or config.get("openai_api_key"))
        
        elif provider_type == "qwen":
            return QwenProvider(api_key=config.get("dashscope_api_key") or config.get("openai_api_key"))
            
        else:
            raise ValueError(f"Unsupported AI Provider: {provider_type}")
            
    except Exception as e:
        print(f"Error initializing {provider_type}: {e}")
        # Fallback to OpenAI if primary fails? Or just raise.
        # For now, let's raise to alert the user configuration is wrong.
        raise e

async def summarize_content(content: str) -> Dict[str, Any]:
    """
    使用當前設定的 AI Provider 生成摘要
    """
    provider = get_llm_provider()
    return await provider.generate_summary(content)

async def chat_with_ai(messages: List[Dict[str, str]]) -> str:
    """
    使用當前設定的 AI Provider 進行對話
    """
    provider = get_llm_provider()
    return await provider.chat(messages)

async def extract_salesforce_info(content: str) -> Dict[str, Any]:
    """
    使用當前設定的 AI Provider 提取 CRM 資訊
    """
    provider = get_llm_provider()
    return await provider.extract_crm_info(content)
