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

function takeText(el) {
  return el ? (el.innerText || el.textContent || '').trim() : '';
}

function extractXPostContent() {
  var text = '';
  var article = document.querySelector('article[data-testid="tweet"]') || document.querySelector('article');
  if (article) {
    text = takeText(article.querySelector('[data-testid="tweetText"]'));
    if (!text) text = takeText(article.querySelector('div[lang]'));
    if (!text) {
      var langEls = article.querySelectorAll('[lang]');
      for (var i = 0; i < langEls.length; i++) {
        var t = takeText(langEls[i]);
        if (t && t.length > 10) { text = t; break; }
      }
    }
    if (!text) text = takeText(article.querySelector('[data-testid="tweetText"]'));
  }
  if (!text) text = takeText(document.querySelector('[data-testid="tweetText"]'));
  if (!text) text = takeText(document.querySelector('div[data-testid="tweetText"]'));
  return text || '';
}

function extractArticleContent() {
  var selectors = [
    'article',
    '[role="article"]',
    'main',
    '[role="main"]',
    '.article-body', '.article-content', '.post-content', '.entry-content',
    '.content-body', '.story-body', '.news-body', '.post-body',
    '.ArticleBody', '.article__body', '.news-content', '.article__content',
    '.story-content', '.RichTextStoryBody', '.teaser-content',
    '#article-body', '#content', '#main-content', '#articleContent',
    '[data-role="articleBody"]', '[itemprop="articleBody"]',
    'div[class*="article"]', 'div[class*="story"]', 'div[class*="content"]'
  ];
  var best = '';
  var title = takeText(document.querySelector('h1')) || takeText(document.querySelector('title')) || '';
  for (var i = 0; i < selectors.length; i++) {
    var el = document.querySelector(selectors[i]);
    if (!el) continue;
    var t = takeText(el);
    if (t && t.length > 200 && t.length > best.length) best = t;
  }
  if (best) return (title ? title + '\n\n' : '') + best;
  var body = document.body;
  if (body) {
    var bodyText = takeText(body);
    if (bodyText && bodyText.length > 300) return (title ? title + '\n\n' : '') + bodyText;
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
      try {
        var base = await getApiBase();
        var res = await fetch(base + '/ingest/text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: 'Source: ' + url + '\n\n(貼文內容無法自動擷取，請在筆記中手動貼上或從「快速筆記」貼上後再存一筆)',
            source_url: url
          })
        });
        var data = await res.json().catch(function() { return {}; });
        if (res.ok) {
          showMessage('已存入連結；請到「筆記」中開啟該則，手動貼上貼文內容。', 'success');
          btn.disabled = false;
          return;
        }
      } catch (e) {}
      showMessage('無法擷取貼文內容。已嘗試僅存連結；若失敗請將網址與內容貼到「快速筆記」存入。', 'error');
      btn.disabled = false;
      return;
    }

    var pageContent = '';
    try {
      var tab = (await chrome.tabs.query({ active: true, currentWindow: true }))[0];
      if (tab && tab.id) {
        var r = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: extractArticleContent
        });
        pageContent = (r && r[0] && r[0].result) ? r[0].result : '';
      }
    } catch (e) {}
    if (pageContent && pageContent.length > 150) {
      var res = await fetch(`${base}/ingest/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: 'Source: ' + url + '\n\n' + pageContent, source_url: url })
      });
      var data = await res.json().catch(() => ({}));
      if (res.ok) {
        showMessage('已從頁面擷取內容並存入第二大腦 ✓');
        btn.disabled = false;
        return;
      }
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
