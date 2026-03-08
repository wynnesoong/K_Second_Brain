from typing import List
from fastapi import APIRouter, HTTPException, Depends
from backend.models.search import SearchRequest, SearchResult, AskRequest, AskResponse
from backend.services.search import SearchService
from backend.services import ai_service
from backend.config import settings

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", response_model=List[SearchResult])
async def search_notes(q: str):
    """
    搜尋本地筆記庫
    """
    service = SearchService()
    results = await service.search_notes(q)
    
    # Convert dict to SearchResult
    return [
        SearchResult(
            title=res["title"],
            path=res["path"],
            snippet=res["snippet"]
        ) for res in results
    ]

@router.post("/ask", response_model=AskResponse)
async def ask_ai(request: AskRequest):
    """
    RAG 問答：先搜尋相關筆記，再讓 AI 回答
    """
    search_service = SearchService()
    results = await search_service.search_notes(request.query)
    
    # Construct Context
    context = ""
    sources = []
    
    for idx, res in enumerate(results[:5]): # Take top 5
        context += f"--- Source {idx+1}: {res['title']} ---\n"
        context += f"{res['snippet']}\n\n"
        sources.append({"file": res["path"], "title": res["title"]})
        
    system_prompt = f"""
    你是 Kevin 的第二大腦助手。請根據以下筆記內容回答使用者的問題。
    若筆記中沒有答案，請誠實告知，並嘗試根據你的通用知識回答但需註明。
    
    相關筆記內容：
    {context}
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    # Add history (last 5 messages to save context window)
    messages.extend(request.history[-5:])
    # Add current question
    messages.append({"role": "user", "content": request.query})
    
    answer = await ai_service.chat_with_ai(messages)
    
    return AskResponse(
        answer=answer,
        sources=sources,
        context_used=len(sources),
        model_used=settings.ai_provider
    )
