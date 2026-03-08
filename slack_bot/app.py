import os
import logging
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import httpx
from dotenv import load_dotenv

# Load env
load_dotenv()

# Config
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
BACKEND_URL = "http://backend:8000" # Docker service name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    try:
        # 簡單的首頁 View
        await client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to Kevin's Second Brain!* :brain:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "你可以直接傳送網址或文字給我，我會自動整理存入 Obsidian。"
                        }
                    },
                     {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "指令：\n- `/search [關鍵字]` : 搜尋筆記\n- `/ask [問題]` : 問答 (RAG)"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.message()
async def handle_message(message, say):
    text = message.get("text", "")
    user = message.get("user")
    
    # 檢查是否為 Salesforce 轉發 (簡單判斷)
    if "Opportunity:" in text or "Amount:" in text:
        # Call Backend Ingest Salesforce
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/ingest/salesforce/message",
                    json={"message": text, "sender": user}
                )
                if response.status_code == 200:
                    data = response.json()
                    await say(f":white_check_mark: Salesforce 商機已存入 CRM！\n摘要: {data.get('summary')}")
                else:
                    await say(f":x: 儲存失敗: {response.text}")
            except Exception as e:
                await say(f":x: 連線錯誤: {e}")
        return

    # 一般訊息：判斷是 URL 還是純文字
    endpoint = "/ingest/url" if text.startswith("http") else "/ingest/text"
    payload = {"url": text} if text.startswith("http") else {"text": text}
    
    # 傳送 "處理中" 反應
    # await app.client.reactions_add(name="thinking_face", channel=message["channel"], timestamp=message["ts"])
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}{endpoint}",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                await say(f":memo: 筆記已儲存！\n標題: {data.get('file_path').split('/')[-1]}\n摘要: {data.get('summary')}")
            else:
                await say(f":x: 處理失敗: {response.text}")
        except Exception as e:
            await say(f":x: 連線後端錯誤: {e}")

@app.command("/search")
async def handle_search_command(ack, body, say):
    await ack()
    query = body.get("text", "")
    if not query:
        await say("請輸入搜尋關鍵字，例如 `/search AI`")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BACKEND_URL}/search/",
                params={"q": query}
            )
            if response.status_code == 200:
                results = response.json()
                if not results:
                    await say(f"找不到關於 `{query}` 的筆記。")
                    return
                
                blocks = [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"找到 {len(results)} 筆關於 `{query}` 的結果："}
                    }
                ]
                
                for res in results[:5]:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{res['path']}|{res['title']}>*\n{res['snippet']}"
                        }
                    })
                
                await say(blocks=blocks)
            else:
                await say(f":x: 搜尋失敗: {response.text}")
        except Exception as e:
            await say(f":x: 連線錯誤: {e}")

@app.command("/ask")
async def handle_ask_command(ack, body, say):
    await ack()
    query = body.get("text", "")
    if not query:
        await say("請輸入問題，例如 `/ask 第二大腦是什麼？`")
        return

    msg = await say(f":thinking_face: 正在思考 `{query}` ... (使用模型: {os.getenv('AI_PROVIDER', 'Unknown')})")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/search/ask",
                json={"query": query, "history": []}
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer")
                sources = data.get("sources", [])
                
                source_text = "\n".join([f"- {s['title']}" for s in sources])
                
                await app.client.chat_update(
                    channel=body["channel_id"],
                    ts=msg["ts"],
                    text=f"{answer}\n\n*參考來源：*\n{source_text}"
                )
            else:
                await app.client.chat_update(
                    channel=body["channel_id"],
                    ts=msg["ts"],
                    text=f":x: 回答失敗: {response.text}"
                )
        except Exception as e:
            await app.client.chat_update(
                channel=body["channel_id"],
                ts=msg["ts"],
                text=f":x: 連線錯誤: {e}"
            )

async def main():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
