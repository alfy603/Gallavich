from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.sql_agent import SQLAgent

router = APIRouter(prefix="/ai-search", tags=["ai-search"])

class SearchRequest(BaseModel):
    question: str

class SearchResponse(BaseModel):
    success: bool
    question: str
    sql_v1: str
    sql_v2: Optional[str] = None
    final_sql: str
    data: List[Dict[str, Any]]
    explanation: str
    reflection: str
    error: Optional[str] = None

@router.post("/search", response_model=SearchResponse)
async def ai_search(request: SearchRequest):
    """
    AI智能搜索接口
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    try:
        agent = SQLAgent()
        result = agent.search(request.question)
        
        return SearchResponse(
            success=result.get("success", False),
            question=request.question,
            sql_v1=result.get("sql_v1", ""),
            sql_v2=result.get("sql_v2"),
            final_sql=result.get("final_sql", ""),
            data=result.get("data", []),
            explanation=result.get("explanation", ""),
            reflection=result.get("reflection", ""),
            error=result.get("error")
        )
    except Exception as e:
        print(f"AI搜索异常: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")