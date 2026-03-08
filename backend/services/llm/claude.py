from typing import Dict, List, Any
import json
from anthropic import AsyncAnthropic
from .base import LLMProvider

class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude Implementation
    寫作自然，Coding 強。
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is required for Claude Provider")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"

    async def generate_summary(self, content: str) -> Dict[str, Any]:
        """
        使用 Claude 生成摘要
        """
        system_prompt = "你是專業的筆記整理助手。請閱讀使用者提供的內容，生成摘要、標籤、分類與待辦事項。回傳純 JSON 格式，不要有 Markdown。"
        user_prompt = f"內容：\n{content}\n\n請回傳 JSON: {{ 'summary': str, 'tags': list, 'category': str, 'action_items': list }}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            # 處理 Claude 回傳，雖然通常很乖，但保險起見
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text.strip())
        except Exception as e:
            print(f"Claude Summary Error: {e}")
            return {"summary": "Error generating summary", "tags": [], "category": "Error", "action_items": []}

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Claude Chat
        """
        # Claude API 不接受 system role 在 messages 列表
        system_msg = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append(msg)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_msg,
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    async def extract_crm_info(self, content: str) -> Dict[str, Any]:
        """
        提取 CRM 資訊
        """
        system_prompt = "你是 Salesforce 資料擷取專家。請從訊息中提取商機資訊。回傳純 JSON。"
        user_prompt = f"訊息：\n{content}\n\n請回傳 JSON: {{ 'title': str, 'amount': str, 'stage': str, 'account': str, 'next_step': str }}"
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except Exception as e:
            print(f"Claude CRM Extract Error: {e}")
            return {}
