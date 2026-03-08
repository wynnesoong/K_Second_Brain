import ollama
from typing import Dict, List, Any
import json
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    """
    Ollama Implementation (Local deployment)
    隱私最高，完全本地端。
    """
    def __init__(self, base_url: str):
        # Ollama library uses OLLAMA_HOST env var primarily, but client can take host
        self.client = ollama.AsyncClient(host=base_url)
        self.model = "llama3" # Default, or from env

    async def generate_summary(self, content: str) -> Dict[str, Any]:
        """
        使用 Ollama 生成摘要
        """
        system_prompt = "你是專業的筆記整理助手。請閱讀使用者提供的內容，生成摘要、標籤、分類與待辦事項。回傳純 JSON 格式。"
        user_prompt = f"內容：\n{content}\n\n請回傳 JSON: {{ 'summary': str, 'tags': list, 'category': str, 'action_items': list }}"

        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format="json" # Ollama supports JSON mode
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"Ollama Summary Error: {e}")
            return {"summary": "Error generating summary", "tags": [], "category": "Error", "action_items": []}

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Ollama Chat
        """
        try:
            response = await self.client.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"

    async def extract_crm_info(self, content: str) -> Dict[str, Any]:
        """
        提取 CRM 資訊
        """
        system_prompt = "你是 Salesforce 資料擷取專家。請從訊息中提取商機資訊。回傳純 JSON。"
        user_prompt = f"訊息：\n{content}\n\n請回傳 JSON: {{ 'title': str, 'amount': str, 'stage': str, 'account': str, 'next_step': str }}"
        
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format="json"
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"Ollama CRM Extract Error: {e}")
            return {}
