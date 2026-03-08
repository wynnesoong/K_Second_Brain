import os
import re
from typing import List, Dict, Any, Optional
from backend.config import settings


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    """從 Markdown 內容取出 YAML frontmatter 的常用欄位。"""
    data = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return data
    block = match.group(1)
    for line in block.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip('"\'')
            if key == "tags" and val.startswith("["):
                data["tags"] = re.findall(r'"([^"]*)"', val) or re.findall(r"'([^']*)'", val)
            else:
                data[key] = val
    return data


def _parse_title_from_content(content: str) -> str:
    """取第一個 # 標題作為 title。"""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    return ""


class NotesService:
    def __init__(self):
        self.vault_path = settings.obsidian_vault_path
        self.folders = ["inbox", "notes", "crm"]

    def list_notes(
        self,
        page: int = 1,
        limit: int = 20,
        folder: Optional[str] = None,
        sort: str = "date_desc",
    ) -> Dict[str, Any]:
        """
        列出筆記，支援分頁。folder: inbox | notes | crm | all
        """
        folders_to_scan = [folder] if folder and folder in self.folders else self.folders
        all_notes: List[Dict[str, Any]] = []

        for fold in folders_to_scan:
            dir_path = os.path.join(self.vault_path, fold)
            if not os.path.isdir(dir_path):
                continue
            for name in os.listdir(dir_path):
                if not name.endswith(".md"):
                    continue
                file_path = os.path.join(dir_path, name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw = f.read()
                except Exception:
                    continue
                fm = _parse_frontmatter(raw)
                title = fm.get("title") or _parse_title_from_content(raw) or name.replace(".md", "")
                date_saved = fm.get("date_saved", "")
                tags = fm.get("tags", [])
                if isinstance(tags, str):
                    tags = [tags]
                summary = (raw.split("##")[1].strip().split("\n")[0][:120] + "…") if "##" in raw else ""
                all_notes.append({
                    "file": name,
                    "folder": fold,
                    "title": title,
                    "summary": summary or "",
                    "tags": tags,
                    "date_saved": date_saved,
                    "status": "inbox" if fold == "inbox" else "processed",
                })

        if sort == "date_desc":
            all_notes.sort(key=lambda x: x.get("date_saved") or "", reverse=True)
        elif sort == "date_asc":
            all_notes.sort(key=lambda x: x.get("date_saved") or "")

        total = len(all_notes)
        start = (page - 1) * limit
        notes = all_notes[start : start + limit]

        return {"page": page, "total": total, "notes": notes}

    def get_note(self, filename: str) -> Optional[Dict[str, Any]]:
        """取得單一筆記內容，會在各資料夾尋找該檔名。"""
        for fold in self.folders:
            file_path = os.path.join(self.vault_path, fold, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw = f.read()
                except Exception:
                    return None
                fm = _parse_frontmatter(raw)
                content = raw
                if raw.startswith("---"):
                    parts = re.split(r"\n---\s*\n", raw, 2)
                    if len(parts) >= 3:
                        content = parts[2]
                return {
                    "file": filename,
                    "folder": fold,
                    "frontmatter": fm,
                    "content": content.strip(),
                }
        return None
