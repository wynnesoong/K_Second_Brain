import os
import re
from datetime import datetime
from typing import List, Dict, Any
from backend.config import settings

class ObsidianWriter:
    def __init__(self):
        self.vault_path = settings.obsidian_vault_path
        self._ensure_directories()

    def _ensure_directories(self):
        """確保 Obsidian 資料夾結構存在"""
        folders = ["inbox", "notes", "crm", "sources", "index"]
        for folder in folders:
            os.makedirs(os.path.join(self.vault_path, folder), exist_ok=True)

    def _sanitize_filename(self, title: str) -> str:
        """
        將標題轉換為合法的檔名 (依據規範：小寫、底線、保留中文)
        """
        # 移除非法字元，保留中文、英文、數字、底線、連字號
        # 簡單做法：替換空格為底線，移除其他特殊符號
        title = title.strip().replace(" ", "_")
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        return title.lower()

    async def save_note(self, title: str, content: str, metadata: Dict[str, Any], folder: str = "notes") -> str:
        """
        儲存筆記到 Obsidian
        
        Args:
            title: 筆記標題
            content: 筆記內容 (Markdown)
            metadata: Frontmatter 資料 (tags, date, url, etc.)
            folder: 目標資料夾 (inbox, notes, crm)
            
        Returns:
            str: 檔案絕對路徑
        """
        safe_title = self._sanitize_filename(title)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{safe_title}.md"
        file_path = os.path.join(self.vault_path, folder, filename)
        
        # 建構 Frontmatter
        frontmatter = "---\n"
        frontmatter += f"title: \"{title}\"\n"
        frontmatter += f"date_saved: \"{date_str}\"\n"
        
        for key, value in metadata.items():
            if key == "tags" and isinstance(value, list):
                frontmatter += f"tags: {value}\n"
            elif key == "summary":
                # Summary 放在內文，不放 Frontmatter 以免過長
                continue
            else:
                frontmatter += f"{key}: \"{value}\"\n"
        
        frontmatter += "---\n\n"
        
        # 組合內容
        full_content = frontmatter
        full_content += f"# {title}\n\n"
        
        if "summary" in metadata:
            full_content += "## AI 摘要\n"
            full_content += f"{metadata['summary']}\n\n"
            
        if "action_items" in metadata and metadata["action_items"]:
            full_content += "## 待辦事項\n"
            for item in metadata["action_items"]:
                full_content += f"- [ ] {item}\n"
            full_content += "\n"
            
        full_content += "## 原始內容\n"
        full_content += content
        
        # 寫入檔案
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            return file_path
        except Exception as e:
            print(f"Error saving note: {e}")
            raise e

    async def save_crm_note(self, crm_data: Dict[str, Any], original_message: str) -> str:
        """
        儲存 Salesforce CRM 筆記
        """
        title = f"CRM: {crm_data.get('account', 'Unknown')} - {crm_data.get('title', 'Untitled')}"
        
        metadata = {
            "type": "salesforce_opportunity",
            "source": "slack_forward",
            "account": crm_data.get("account", ""),
            "amount": crm_data.get("amount", "0"),
            "stage": crm_data.get("stage", ""),
            "tags": ["CRM", "商機", crm_data.get("account", "")]
        }
        
        # 格式化原始訊息引用
        formatted_content = "> " + original_message.replace("\n", "\n> ")
        
        return await self.save_note(title, formatted_content, metadata, folder="crm")
