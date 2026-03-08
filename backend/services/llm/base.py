from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class LLMProvider(ABC):
    """
    抽象基礎類別：所有 AI Provider 都必須實作此介面。
    支援 10 種模型：Gemini, OpenAI, Ollama, Claude, DeepSeek, Mistral, Groq, OpenRouter, Kimi, Qwen
    """
    
    @abstractmethod
    async def generate_summary(self, content: str) -> Dict[str, Any]:
        """
        生成內容摘要
        
        Args:
            content (str): 原始文字內容
            
        Returns:
            Dict[str, Any]: {
                "summary": str,  # 摘要內容
                "tags": List[str],  # 建議標籤
                "category": str,  # 建議分類
                "action_items": List[str] # 待辦事項 (若有)
            }
        """
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        對話功能
        
        Args:
            messages (List[Dict[str, str]]): 對話歷史 [{"role": "user", "content": "..."}, ...]
            
        Returns:
            str: AI 回覆文字
        """
        pass

    @abstractmethod
    async def extract_crm_info(self, content: str) -> Dict[str, Any]:
        """
        從文字中提取 CRM 資訊 (針對 Slack 轉發的 Salesforce 訊息)
        
        Args:
            content (str): 包含 CRM 資訊的文字
            
        Returns:
            Dict[str, Any]: {
                "title": str,
                "amount": str,
                "stage": str,
                "account": str,
                "next_step": str
            }
        """
        pass
