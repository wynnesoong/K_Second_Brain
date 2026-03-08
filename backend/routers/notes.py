from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.services.notes_service import NotesService

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("")
async def list_notes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    folder: Optional[str] = Query(None, description="inbox | notes | crm"),
    sort: str = Query("date_desc", description="date_desc | date_asc"),
):
    """列出筆記，支援分頁與資料夾篩選。"""
    service = NotesService()
    return service.list_notes(page=page, limit=limit, folder=folder, sort=sort)


@router.get("/tags/list")
async def list_tags():
    """列出所有標籤及使用次數。"""
    service = NotesService()
    return {"tags": service.get_tags()}


@router.get("/{filename}")
async def get_note(filename: str):
    """取得單一筆記完整內容。"""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    service = NotesService()
    note = service.get_note(filename)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
