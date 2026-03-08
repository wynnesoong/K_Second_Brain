from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    title: str
    path: str
    snippet: str
    score: float = 0.0

class AskRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = [] # [{"role": "user", "content": "..."}]

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: int
    model_used: str
