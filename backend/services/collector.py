import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any

class CollectorService:
    def __init__(self):
        self.client = httpx.AsyncClient(headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })

    async def fetch_url(self, url: str) -> Dict[str, str]:
        """
        抓取 URL 內容並提取標題與內文
        """
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 簡單提取標題
            title = soup.title.string if soup.title else url
            
            # 簡單提取內文 (移除 script, style)
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator="\n", strip=True)
            
            return {
                "url": url,
                "title": title,
                "content": text[:10000] # 限制長度以免爆 Token
            }
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {"url": url, "title": "Error fetching", "content": str(e)}

    async def close(self):
        await self.client.aclose()
