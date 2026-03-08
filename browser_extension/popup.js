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
