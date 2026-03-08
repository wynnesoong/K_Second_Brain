# Kevin 第二大腦系統｜API 接口文件
**版本：** v1.5  
**日期：** 2026-03-08  
**Base URL：** `http://localhost:8000`  
**認證：** 目前為本地使用，無需 Token（第二期視需求加入）

---

## 一、收集端點

### POST /ingest/url
收集網址內容，自動抓取並存入 Obsidian。

**請求：**
```json
{
  "url": "https://example.com/article",
  "note": "這是 Kevin 附加的備註（選填）"
}
```

**回應（成功 200）：**
```json
{
  "status": "success",
  "file": "2026-03-06_article-title.md",
  "title": "文章標題",
  "summary": "AI 生成的摘要內容",
  "tags": ["機器視覺", "AI", "技術"],
  "category": "技術",
  "vault_path": "/obsidian_vault/inbox/2026-03-06_article-title.md",
  "drive_sync_status": "queued"
}
```

**回應（失敗 400）：**
```json
{
  "status": "error",
  "message": "無法抓取該網址內容",
  "url": "https://example.com/article"
}
```

---

### POST /ingest/text
手動貼文字存入，適用於 AI 整理資料、截圖文字、自己打的筆記。

**請求：**
```json
{
  "content": "要存入的文字內容",
  "title": "自訂標題（選填，不填 AI 自動生成）",
  "source": "來源說明（選填，如：ChatGPT 整理、會議記錄）",
  "tags": ["自訂標籤1", "自訂標籤2"]
}
```

**回應（成功 200）：**
```json
{
  "status": "success",
  "file": "2026-03-06_自訂標題.md",
  "title": "自訂標題",
  "summary": "AI 生成的摘要",
  "tags": ["自訂標籤1", "自訂標籤2", "AI補充標籤"],
  "category": "個人",
  "vault_path": "/obsidian_vault/inbox/2026-03-06_自訂標題.md",
  "drive_sync_status": "queued"
}
```

---

### POST /ingest/x_post
收集 X（Twitter）貼文內容。

**請求：**
```json
{
  "url": "https://x.com/username/status/1234567890",
  "note": "備註（選填）"
}
```

**回應（成功 200）：**
```json
{
  "status": "success",
  "file": "2026-03-06_x-username-1234567890.md",
  "author": "@username",
  "content_preview": "貼文前100字...",
  "tags": ["X", "AI", "觀點"],
  "vault_path": "/obsidian_vault/inbox/2026-03-06_x-username-1234567890.md",
  "drive_sync_status": "queued"
}
```

---

### POST /ingest/salesforce/message
接收從 Slack 轉發的 Salesforce 訊息內容。

**請求：**
```json
{
  "content": "New Opportunity: TSMC ... (Slack message content)",
  "sender": "U12345678"
}
```

**回應（成功 200）：**
```json
{
  "status": "success",
  "synced_count": 1,
  "files": [
    "CRM_TSMC_Expansion.md"
  ]
}
```

---

## 二、Google Drive 同步端點

### POST /export/drive/{filename}
手動觸發單一筆記同步至 Google Drive（NotebookLM 來源）。通常由系統自動呼叫，此端點用於手動重試。

**請求：**
```
POST /export/drive/2026-03-06_article-title.md
```

**回應（成功 200）：**
```json
{
  "status": "success",
  "file": "2026-03-06_article-title.md",
  "drive_file_id": "1A2B3C4D5E...",
  "drive_url": "https://docs.google.com/document/d/...",
  "format": "google_doc"
}
```

---

## 三、查詢端點

### GET /search
全文搜尋筆記庫，回傳最相關結果。

**請求參數：**
```
GET /search?q=機器視覺應用&limit=10&category=技術
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| q | string | 是 | 搜尋關鍵字 |
| limit | int | 否 | 回傳筆數，預設 10，最大 50 |
| category | string | 否 | 篩選分類：技術/業務/個人/其他 |
| tags | string | 否 | 篩選標籤（逗號分隔） |
| date_from | string | 否 | 開始日期 YYYY-MM-DD |
| date_to | string | 否 | 結束日期 YYYY-MM-DD |

**回應（成功 200）：**
```json
{
  "query": "機器視覺應用",
  "total": 23,
  "results": [
    {
      "file": "2026-02-15_machine-vision-trends.md",
      "title": "2026 機器視覺趨勢",
      "summary": "文章摘要...",
      "tags": ["機器視覺", "趨勢", "工業"],
      "category": "技術",
      "date_saved": "2026-02-15",
      "source": "https://example.com",
      "relevance_score": 0.92,
      "snippet": "...含有關鍵字的段落片段..."
    }
  ]
}
```

---

### POST /ask
自然語言問答，AI 根據筆記庫內容回答。

**請求：**
```json
{
  "question": "我存過哪些關於機器視覺的資料？",
  "context_limit": 20
}
```

**回應（成功 200）：**
```json
{
  "answer": "根據你的筆記，你存過以下關於機器視覺的資料：\n1. ...\n2. ...",
  "sources": [
    {
      "file": "2026-02-15_machine-vision-trends.md",
      "title": "2026 機器視覺趨勢",
      "date_saved": "2026-02-15"
    }
  ],
  "context_used": 15,
  "model_used": "kimi-v1"
}
```

---

### GET /notes
列出所有筆記，支援分頁與篩選。

**請求參數：**
```
GET /notes?page=1&limit=20&category=技術&status=inbox
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| page | int | 否 | 頁碼，預設 1 |
| limit | int | 否 | 每頁筆數，預設 20 |
| category | string | 否 | 篩選分類 |
| status | string | 否 | inbox / processed |
| sort | string | 否 | date_desc（預設）/ date_asc / relevance |

**回應（成功 200）：**
```json
{
  "page": 1,
  "total": 156,
  "notes": [
    {
      "file": "2026-03-06_article-title.md",
      "title": "文章標題",
      "summary": "摘要...",
      "tags": ["標籤1"],
      "category": "技術",
      "date_saved": "2026-03-06",
      "status": "inbox"
    }
  ]
}
```

---

### GET /notes/{filename}
取得單一筆記完整內容。

**請求：**
```
GET /notes/2026-03-06_article-title.md
```

**回應（成功 200）：**
```json
{
  "file": "2026-03-06_article-title.md",
  "frontmatter": {
    "title": "文章標題",
    "source": "https://...",
    "tags": ["標籤1"],
    "category": "技術",
    "date_saved": "2026-03-06"
  },
  "content": "完整 Markdown 內容..."
}
```

---

### GET /tags
列出所有標籤及使用次數。

**回應（成功 200）：**
```json
{
  "tags": [
    { "name": "機器視覺", "count": 23 },
    { "name": "AI", "count": 45 },
    { "name": "業務", "count": 12 }
  ]
}
```

---

## 四、系統端點

### GET /health
系統健康檢查。

**回應（成功 200）：**
```json
{
  "status": "healthy",
  "vault_path": "/obsidian_vault",
  "total_notes": 156,
  "db_status": "ok",
  "ai_provider": "kimi",
  "google_drive_api": "ok"
}
```

### POST /reindex
重建 SQLite 全文搜尋索引（維護用）。

**回應（成功 200）：**
```json
{
  "status": "success",
  "indexed": 156,
  "duration_seconds": 3.2
}
```

---

## 五、錯誤碼一覽

| HTTP 狀態碼 | 錯誤類型 | 說明 |
|-------------|----------|------|
| 400 | Bad Request | 請求格式錯誤或缺少必填欄位 |
| 404 | Not Found | 筆記不存在 |
| 422 | Validation Error | 參數驗證失敗（FastAPI 預設） |
| 429 | Too Many Requests | AI API 速率限制 |
| 500 | Internal Server Error | 後端錯誤，查看 logs |
| 503 | Service Unavailable | AI API 或 Google Drive API 無法連線 |

---

## 六、Slack Bot 指令規範

| 指令 | 說明 | 範例 |
|------|------|------|
| `存 [網址]` | 存入網址 | `存 https://example.com` |
| `存 [文字]` | 存入文字筆記 | `存 今天客戶說希望增加AOI功能` |
| `問 [問題]` | 問答查詢 | `問 我存過哪些關於AOI的資料` |
| `找 [關鍵字]` | 關鍵字搜尋 | `找 機器視覺` |
| `最新` | 列出最近10筆筆記 | `最新` |
| `[轉發 Salesforce 訊息]` | 解析並存入 CRM 資料夾 | *(直接轉發 Slack 訊息)* |

---

*本文件為 API 憲法。新增或修改端點需先更新本文件，再動 code。*
