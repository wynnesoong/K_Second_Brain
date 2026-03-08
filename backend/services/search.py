import os
from typing import List, Dict, Any
from backend.config import settings

class SearchService:
    def __init__(self):
        self.vault_path = settings.obsidian_vault_path

    async def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """
        簡單搜尋筆記內容 (grep-like)
        未來應替換為 SQLite FTS5 全文檢索
        """
        results = []
        # Walk through vault
        for root, dirs, files in os.walk(self.vault_path):
            if ".obsidian" in root or ".git" in root or ".trash" in root:
                continue
                
            for file in files:
                if not file.endswith(".md"):
                    continue
                
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    if query.lower() in content.lower():
                        # Extract title from filename or content
                        title = file.replace(".md", "").replace("_", " ")
                        
                        # Simple snippet
                        idx = content.lower().find(query.lower())
                        start = max(0, idx - 50)
                        end = min(len(content), idx + 100)
                        snippet = content[start:end].replace("\n", " ")
                        
                        results.append({
                            "title": title,
                            "path": file_path,
                            "snippet": f"...{snippet}..."
                        })
                        
                        if len(results) >= 10: # Limit results
                            return results
                except Exception:
                    continue
                    
        return results
