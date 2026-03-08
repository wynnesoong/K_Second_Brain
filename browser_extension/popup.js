const DEFAULT_API_BASE = 'http://localhost:8000';

async function getApiBase() {
  const { apiBase } = await chrome.storage.local.get({ apiBase: DEFAULT_API_BASE });
  return apiBase.replace(/\/$/, '');
}

function showMessage(text, type = 'success') {
  const el = document.getElementById('message');
  el.textContent = text;
  el.className = 'message ' + type;
  el.setAttribute('aria-live', 'polite');
}

function extractXPostContent() {
  var sel = document.querySelector('[data-testid="tweetText"]');
  if (sel && sel.innerText) return sel.innerText.trim();
  var article = document.querySelector('article');
  if (article) {
    var textEl = article.querySelector('[lang]');
    if (textEl && textEl.innerText) return textEl.innerText.trim();
  }
  return '';
}

async function saveUrl() {
  const btn = document.getElementById('saveUrlBtn');
  const url = document.getElementById('currentUrl').textContent;
  if (!url || url === '讀取中…' || url.startsWith('chrome://') || url.startsWith('edge://')) {
    showMessage('此頁面無法儲存（僅支援一般網址）', 'error');
    return;
  }
  btn.disabled = true;
  showMessage('儲存中…');
  try {
    const base = await getApiBase();
    const isX = /^https:\/\/(x\.com|twitter\.com)\//.test(url);

    if (isX) {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.id) {
          const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: extractXPostContent
          });
          const tweetText = results && results[0] && results[0].result ? results[0].result : '';
          if (tweetText) {
            const res = await fetch(`${base}/ingest/text`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: 'Source: ' + url + '\n\n' + tweetText, source_url: url })
            });
            const data = await res.json().catch(() => ({}));
            if (res.ok) {
              showMessage('X 貼文已存入第二大腦 ✓');
              btn.disabled = false;
              return;
            }
            showMessage(data.detail || data.message || '儲存失敗', 'error');
            btn.disabled = false;
            return;
          }
        }
      } catch (scriptErr) {
        console.warn('X extract failed', scriptErr);
      }
      showMessage('無法擷取貼文內容，請確認在貼文頁面並重新整理後再試；或將內容複製到「快速筆記」存入。', 'error');
      btn.disabled = false;
      return;
    }

    const res = await fetch(`${base}/ingest/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      showMessage('已存入第二大腦 ✓');
    } else {
      showMessage(data.detail || data.message || '儲存失敗', 'error');
    }
  } catch (e) {
    getApiBase().then(base => {
      const msg = e.message || '';
      let tip = '請到擴充功能「設定」檢查 API 網址。';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        tip = '連線被拒絕或逾時：請確認後端已啟動，且若後端在另一台電腦（如 Win11），請在設定中填 http://該電腦IP:8000';
      }
      showMessage(`${tip} 目前網址：${base}`, 'error');
    });
  } finally {
    btn.disabled = false;
  }
}

async function saveText() {
  const btn = document.getElementById('saveTextBtn');
  const text = document.getElementById('quickNote').value.trim();
  if (!text) {
    showMessage('請輸入或貼上文字', 'error');
    return;
  }
  btn.disabled = true;
  showMessage('儲存中…');
  try {
    const base = await getApiBase();
    const res = await fetch(`${base}/ingest/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      showMessage('已存入第二大腦 ✓');
      document.getElementById('quickNote').value = '';
    } else {
      showMessage(data.detail || data.message || '儲存失敗', 'error');
    }
  } catch (e) {
    getApiBase().then(base => {
      const msg = e.message || '';
      let tip = '請到擴充功能「設定」檢查 API 網址。';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        tip = '連線被拒絕或逾時：請確認後端已啟動，且若後端在另一台電腦（如 Win11），請在設定中填 http://該電腦IP:8000';
      }
      showMessage(`${tip} 目前網址：${base}`, 'error');
    });
  } finally {
    btn.disabled = false;
  }
}

document.getElementById('saveUrlBtn').addEventListener('click', saveUrl);
document.getElementById('saveTextBtn').addEventListener('click', saveText);

document.getElementById('optionsLink').addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const tab = tabs[0];
  const urlEl = document.getElementById('currentUrl');
  if (tab && tab.url) {
    urlEl.textContent = tab.url;
  } else {
    urlEl.textContent = '無法取得網址';
  }
});
