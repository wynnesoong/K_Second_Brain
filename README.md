# Kevin 第二大腦系統

這是一個基於 AI (支援 10 種模型)、Obsidian、Slack 與 Salesforce 整合的個人知識管理系統。

## 功能特色
- **多模型 AI 支援**：隨時切換 OpenAI, Gemini, Claude, Kimi, Qwen 等 10 種模型。
- **Slack 整合**：透過 Slack 對話收集資料、查詢筆記，並自動接收 Salesforce CRM 訊息。
- **Obsidian 本地儲存**：所有資料儲存在本地 Markdown 檔案，確保資料主權。
- **NotebookLM 同步**：自動將筆記同步至 Google Drive 供 NotebookLM 讀取。
- **Docker 化部署**：支援 macOS, Windows, Synology NAS 等多平台。

## 快速開始 (Local Development)

1. **複製環境變數設定檔**
   ```bash
   cp .env.example .env
   ```

2. **填寫 `.env` 內容**
   - 填入您的 AI API Keys (例如 `GOOGLE_API_KEY`, `OPENAI_API_KEY` 等)
   - 填入 Slack App Token/Bot Token
   - (選用) 設定 Google Drive 認證

3. **啟動系統**
   ```bash
   docker-compose up --build
   ```

4. **開始使用**
   - Backend API: http://localhost:8000/docs
   - Slack Bot: 在 Slack 中與 Bot 對話

## 目錄結構
- `backend/`: FastAPI 後端服務
- `slack_bot/`: Slack Bolt App
- `obsidian_vault/`: 您的筆記資料夾 (會映射到 Container 內)
- `docker-compose.yml`: 系統啟動設定

詳情請參閱 `DEPLOYMENT.md` 部署手冊。
