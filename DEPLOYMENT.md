# 部署手冊 (Deployment Manual)

本文件說明如何將「Kevin 第二大腦系統」部署至不同環境 (MacOS, Windows, Synology NAS)。

由於系統使用 Docker 封裝，核心邏輯在所有平台上皆一致，唯獨路徑設定與權限需特別注意。

---

## 一、通用準備事項 (所有平台)

1.  **取得程式碼**：將本專案資料夾完整複製到目標機器。
2.  **準備 API Keys**：確保您擁有 `google_api_key`, `openai_api_key` 等必要金鑰。
3.  **設定 `.env`**：
    - 複製 `.env.example` 為 `.env`。
    - 填入您的 API Keys。
    - 設定 `AI_PROVIDER` (例如 `gemini` 或 `openai`)。
    - 若需使用 Google Drive 同步，請將 `credentials.json` 放入專案根目錄。

---

## 二、MacOS 部署 (本機開發/測試)

適用於您的 MacBook Pro 開發環境。

1.  **安裝 Docker Desktop**：
    - 前往 Docker 官網下載並安裝 Docker Desktop for Mac。
    - 啟動 Docker Desktop。

2.  **啟動服務**：
    開啟終端機 (Terminal)，切換到專案目錄：
    ```bash
    cd /path/to/second-brain
    docker-compose up -d --build
    ```

3.  **驗證**：
    - 瀏覽器打開 `http://localhost:8000/docs` 確認後端 API 正常運作。
    - Slack Bot 應顯示上線狀態。

4.  **停止服務**：
    ```bash
    docker-compose down
    ```

---

## 三、Synology NAS (DS918+) 部署

適用於長期運行的生產環境。

1.  **安裝 Container Manager (Docker)**：
    - 在 DSM 套件中心搜尋並安裝 `Container Manager` (舊稱 Docker)。

2.  **上傳檔案**：
    - 使用 File Station 或 SMB，將整個 `second-brain` 資料夾上傳至 NAS 的 `/docker/second-brain` (建議路徑)。
    - 確保 `obsidian_vault` 資料夾也在其中。

3.  **SSH 連線部署 (推薦)**：
    - 開啟 NAS 的 SSH 功能 (控制台 > 終端機)。
    - 使用終端機連線：`ssh admin@nas-ip`
    - 切換到目錄：`cd /volume1/docker/second-brain`
    - 執行部署指令：
      ```bash
      sudo docker-compose up -d --build
      ```

4.  **權限設定**：
    - 若遇到 `obsidian_vault` 無法寫入的問題，請確認 Docker 容器使用者 (通常是 root) 對該資料夾有寫入權限，或在 `docker-compose.yml` 指定 `user: "1026:100"` (配合您的 NAS 用戶 ID)。

---

## 四、Windows 部署

適用於其他 Windows 主機。

1.  **安裝 Docker Desktop for Windows**：
    - 需開啟 WSL 2 (Windows Subsystem for Linux) 功能。
    - 安裝 Docker Desktop 並啟動。

2.  **PowerShell 啟動**：
    - 開啟 PowerShell 或 Command Prompt。
    - 切換到專案目錄：`cd C:\path\to\second-brain`
    - 執行：
      ```powershell
      docker-compose up -d --build
      ```

3.  **注意事項**：
    - Windows 的路徑分隔符號雖為 `\`，但在 `docker-compose.yml` 中仍使用 `/` 或相對路徑 `./` 即可，Docker 會自動處理。
    - 建議使用 Git Bash 或 WSL 終端機操作會更順暢。

---

## 五、常見問題

- **Q: 如何更新程式？**
  A: 下載新版程式碼覆蓋後，執行 `docker-compose build && docker-compose up -d` 重新建置並啟動。

- **Q: 如何備份資料？**
  A: 您的筆記都在 `obsidian_vault` 資料夾中，直接備份該資料夾即可。Docker 容器刪除也不會影響筆記資料。
