from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """
    OpenAI Implementation (Compatible with DeepSeek, Groq, Kimi, Qwen, OpenRouter)
    支援標準 OpenAI API 格式。
    """
    def __init__(
        self, 
        api_key: str, 
        base_url: Optional[str] = None, 
        model_name: str = "gpt-4-turbo"
    ):
        if not api_key:
            raise ValueError("API Key is required for OpenAI Provider")
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def generate_summary(self, content: str) -> Dict[str, Any]:
        """
        使用 OpenAI Compatible API 生成摘要
        """
        system_prompt = "你是專業的筆記整理助手。請閱讀使用者提供的內容，生成摘要、標籤、分類與待辦事項。回傳純 JSON 格式，不要有 Markdown。"
        user_prompt = f"內容：\n{content}\n\n請回傳 JSON: {{ 'summary': str, 'tags': list, 'category': str, 'action_items': list }}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} # 確保回傳 JSON
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI Summary Error: {e}")
            return {"summary": "Error generating summary", "tags": [], "category": "Error", "action_items": []}

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        OpenAI Chat
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    async def extract_crm_info(self, content: str) -> Dict[str, Any]:
        """
        提取 CRM 資訊
        """
        system_prompt = "你是 Salesforce 資料擷取專家。請從訊息中提取商機資訊 (Title, Amount, Stage, Account, Next Step)。回傳純 JSON。"
        user_prompt = f"訊息：\n{content}\n\n請回傳 JSON: {{ 'title': str, 'amount': str, 'stage': str, 'account': str, 'next_step': str }}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI CRM Extract Error: {e}")
            return {}
