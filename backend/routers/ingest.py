from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.ingest import IngestUrlRequest, IngestTextRequest, IngestSalesforceRequest, IngestResponse
from backend.services.collector import CollectorService
from backend.services import ai_service
from backend.services.obsidian_writer import ObsidianWriter

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("/url", response_model=IngestResponse)
async def ingest_url(request: IngestUrlRequest):
    """
    抓取網頁內容，透過 AI 生成摘要，並存入 Obsidian。
    """
    collector = CollectorService()
    try:
        data = await collector.fetch_url(request.url)
        await collector.close()
        
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Unable to fetch content from URL")

        # AI Summary
        summary_data = await ai_service.summarize_content(data["content"])
        
        # Save to Obsidian
        writer = ObsidianWriter()
        metadata = summary_data.copy()
        metadata["url"] = request.url
        metadata["tags"] = summary_data.get("tags", []) + ["WebClip"]
        
        file_path = await writer.save_note(
            title=data.get("title", "Untitled Web Clip"),
            content=data["content"],
            metadata=metadata,
            folder="inbox"
        )
        
        return IngestResponse(
            status="success",
            file_path=file_path,
            summary=summary_data.get("summary"),
            tags=summary_data.get("tags")
        )
    except Exception as e:
        await collector.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text", response_model=IngestResponse)
async def ingest_text(request: IngestTextRequest):
    """
    處理純文字輸入，透過 AI 生成摘要，存入 Obsidian。
    若帶 source_url（如 X 貼文網址）會寫入 frontmatter 並加標籤 XPost。
    """
    try:
        # AI Summary
        summary_data = await ai_service.summarize_content(request.text)
        
        # Save to Obsidian
        writer = ObsidianWriter()
        metadata = summary_data.copy()
        metadata["tags"] = summary_data.get("tags", []) + ["QuickNote"]
        if request.source_url:
            metadata["url"] = request.source_url
            if "x.com" in request.source_url or "twitter.com" in request.source_url:
                metadata["tags"] = summary_data.get("tags", []) + ["XPost", "QuickNote"]
        
        # Generate a title from summary first sentence or first 20 chars
        title = summary_data.get("summary", "")[:20] + "..." if summary_data.get("summary") else "Quick Note"
        
        file_path = await writer.save_note(
            title=title,
            content=request.text,
            metadata=metadata,
            folder="inbox"
        )
        
        return IngestResponse(
            status="success",
            file_path=file_path,
            summary=summary_data.get("summary"),
            tags=summary_data.get("tags")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/salesforce/message", response_model=IngestResponse)
async def ingest_salesforce_message(request: IngestSalesforceRequest):
    """
    接收 Slack 轉發的 Salesforce 訊息，透過 AI 解析並存入 CRM 資料夾。
    """
    try:
        # AI Extract Info
        crm_data = await ai_service.extract_salesforce_info(request.message)
        
        if not crm_data.get("title") and not crm_data.get("account"):
             raise HTTPException(status_code=400, detail="AI could not extract valid CRM info")

        # Save to Obsidian CRM folder
        writer = ObsidianWriter()
        
        # 這裡會使用 save_crm_note 處理特定格式
        file_path = writer.save_crm_note(crm_data, request.message) # save_crm_note needs async await
        
        # wait, save_crm_note IS async in implementation? Check implementation.
        # Yes, I defined it as async def save_crm_note
        file_path = await writer.save_crm_note(crm_data, request.message)

        return IngestResponse(
            status="success",
            file_path=file_path,
            summary=f"Created Opportunity: {crm_data.get('title')}",
            tags=["CRM", "Salesforce"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
