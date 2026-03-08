import google.generativeai as genai
from typing import Dict, List, Any
import json
from .base import LLMProvider
from backend.config import settings

class GeminiProvider(LLMProvider):
    """
    Google Gemini (Pro 1.5) Implementation
    長文本與 RAG 的首選模型。
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google API Key is required for Gemini Provider")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    async def generate_summary(self, content: str) -> Dict[str, Any]:
        """
        使用 Gemini 生成摘要與標籤
        """
        prompt = f"""
        請閱讀以下內容，並生成摘要、標籤、分類與待辦事項。
        請以 JSON 格式回傳，欄位包含：summary, tags (list), category, action_items (list)。
        
        內容：
        {content}
        """
        try:
            response = self.model.generate_content(prompt)
            # 處理可能的回傳格式 (有時會有 ```json 包裹)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text.strip())
        except Exception as e:
            print(f"Gemini Summary Error: {e}")
            return {
                "summary": "無法生成摘要",
                "tags": [],
                "category": "Uncategorized",
                "action_items": []
            }

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Gemini Chat
        """
        # 轉換 OpenAI 格式 messages 到 Gemini History
        gemini_history = []
        last_user_message = ""
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                # Gemini Pro 1.5 支援 System Instruction 但為了簡化，先併入 User 或忽略
                # 這裡暫時忽略或當作第一則 User Message 的前綴
                continue
            
            if msg["role"] == "user":
                last_user_message = msg["content"]
            else:
                gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        # 啟動 Chat Session
        chat = self.model.start_chat(history=gemini_history)
        response = chat.send_message(last_user_message)
        return response.text

    async def extract_crm_info(self, content: str) -> Dict[str, Any]:
        """
        使用 Gemini 提取 Salesforce 資訊
        """
        prompt = f"""
        請從以下 Slack 訊息中提取 Salesforce 商機資訊。
        請以 JSON 格式回傳，欄位包含：title, amount (數值字串), stage, account, next_step (若無則為空字串)。
        
        訊息內容：
        {content}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except Exception as e:
            print(f"Gemini CRM Extract Error: {e}")
            return {}
