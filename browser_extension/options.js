const DEFAULT_API_BASE = 'http://localhost:8000';

function getInputUrl() {
  const input = document.getElementById('apiBase');
  let value = (input.value || '').trim().replace(/\/$/, '');
  if (!value) value = DEFAULT_API_BASE;
  if (!value.startsWith('http://') && !value.startsWith('https://')) {
    value = 'http://' + value;
  }
  return value;
}

function showOptionsMessage(text, type) {
  const msg = document.getElementById('optionsMessage');
  msg.textContent = text;
  msg.className = 'message ' + (type || '');
}

document.getElementById('saveOptions').addEventListener('click', async () => {
  const value = getInputUrl();
  await chrome.storage.local.set({ apiBase: value });
  showOptionsMessage('已儲存', 'success');
  setTimeout(() => { showOptionsMessage(''); }, 2000);
});

document.getElementById('testConnection').addEventListener('click', async () => {
  const base = getInputUrl();
  showOptionsMessage('測試中…');
  try {
    const res = await fetch(base + '/health');
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.status === 'healthy') {
      showOptionsMessage('連線成功 ✓ 後端正常（' + (data.ai_provider || '') + '）', 'success');
    } else {
      showOptionsMessage('後端回傳異常：' + (data.detail || res.status), 'error');
    }
  } catch (e) {
    showOptionsMessage('無法連線：' + (e.message || '請確認網址、後端已啟動、防火牆允許 8000 埠'), 'error');
  }
});

chrome.storage.local.get({ apiBase: DEFAULT_API_BASE }, (data) => {
  document.getElementById('apiBase').value = data.apiBase || DEFAULT_API_BASE;
});
