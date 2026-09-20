const slides = [...document.querySelectorAll('.slide')];

let index = 0;

let notes = false;

let all = false;

const prev = document.querySelector('#prev');

const next = document.querySelector('#next');

const logDialog = document.querySelector('#classlog');

const logText = document.querySelector('#classlog-text');

const logPage = document.querySelector('#classlog-page');

const logStatus = document.querySelector('#classlog-status');

const lessonId = document.body.dataset.lesson || 'lesson';

const LOG_IDB = 'ml-course-slides';

const LOG_STORE = 'kv';

const LOG_CONTENT_KEY = `class-log-content:${lessonId}`;

let logSaveTimer = null;



function normalizeLogText(text) {

  return text.replace(/\r\n/g, '\n');

}



function pageMark(n) {

  return new RegExp(

    `^=== 第 ${n} 页 · .+ ===\\n([\\s\\S]*?)(?=\\n=== 第 \\d+ 页 ·|$)`,

    'm',

  );

}



function extractPageLog(text, pageNum) {

  const m = normalizeLogText(text).match(pageMark(pageNum));

  return m ? m[1].trimEnd() : '';

}



function replacePageLog(text, pageNum, content) {

  const normalized = normalizeLogText(text);

  const re = new RegExp(

    `(^=== 第 ${pageNum} 页 · .+ ===\\n)[\\s\\S]*?(?=\\n=== 第 \\d+ 页 ·|$)`,

    'm',

  );

  if (!re.test(normalized)) return normalized;

  return normalized.replace(re, `$1${content}\n\n`);

}



function buildLogTemplateFromDom() {

  const topic = slides[0]?.querySelector('.topic')?.textContent?.trim() || document.title;

  const lines = [

    `# 课堂记录 · ${topic}`,

    '# 课件内自动保存在浏览器；「导出 class-log.txt」可下载到本讲文件夹。',

    '',

  ];

  slides.forEach((s, i) => {

    const title = s.querySelector('h1')?.textContent?.trim() || `第 ${i + 1} 页`;

    lines.push(`=== 第 ${i + 1} 页 · ${title} ===`, '', '');

  });

  return lines.join('\n');

}



function openIdb() {

  return new Promise((resolve, reject) => {

    const req = indexedDB.open(LOG_IDB, 1);

    req.onupgradeneeded = () => req.result.createObjectStore(LOG_STORE);

    req.onsuccess = () => resolve(req.result);

    req.onerror = () => reject(req.error);

  });

}



async function idbGet(key) {

  const db = await openIdb();

  return new Promise((resolve, reject) => {

    const tx = db.transaction(LOG_STORE, 'readonly');

    const req = tx.objectStore(LOG_STORE).get(key);

    req.onsuccess = () => resolve(req.result);

    req.onerror = () => reject(req.error);

  });

}



async function idbSet(key, value) {

  const db = await openIdb();

  return new Promise((resolve, reject) => {

    const tx = db.transaction(LOG_STORE, 'readwrite');

    tx.objectStore(LOG_STORE).put(value, key);

    tx.oncomplete = () => resolve();

    tx.onerror = () => reject(tx.error);

  });

}



function setLogStatus(msg) {

  if (logStatus) logStatus.textContent = msg;

}



async function getLogDocument() {

  const cached = await idbGet(LOG_CONTENT_KEY);

  if (typeof cached === 'string' && cached.trim()) {

    return normalizeLogText(cached);

  }

  try {

    const res = await fetch('class-log.txt', { cache: 'no-store' });

    if (res.ok) {

      const text = normalizeLogText(await res.text());

      await idbSet(LOG_CONTENT_KEY, text);

      return text;

    }

  } catch (_) {

    /* file:// 下 fetch 不可用，改用浏览器内存储 */

  }

  const templ = buildLogTemplateFromDom();

  await idbSet(LOG_CONTENT_KEY, templ);

  return templ;

}



async function persistCurrentPage() {

  if (!logText) return;

  const base = await getLogDocument();

  const updated = replacePageLog(base, index + 1, logText.value);

  await idbSet(LOG_CONTENT_KEY, updated);

  setLogStatus('已自动保存（本浏览器，关闭后仍可打开查看）');

}



function schedulePersistCurrentPage() {

  clearTimeout(logSaveTimer);

  logSaveTimer = setTimeout(() => {

    void persistCurrentPage();

  }, 400);

}



async function loadPageLog() {

  if (!logText) return;

  try {

    const text = await getLogDocument();

    logText.value = extractPageLog(text, index + 1);

    setLogStatus('已载入；编辑后会自动保存');

  } catch (_) {

    logText.value = '';

    setLogStatus('载入失败，请刷新页面后重试');

  }

}



async function exportLogFile() {

  if (!logText) return;

  try {

    await persistCurrentPage();

    const text = await idbGet(LOG_CONTENT_KEY);

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });

    const a = document.createElement('a');

    a.href = URL.createObjectURL(blob);

    a.download = 'class-log.txt';

    a.click();

    URL.revokeObjectURL(a.href);

    setLogStatus('已下载 class-log.txt，请保存到本讲文件夹（覆盖原文件）');

  } catch (_) {

    setLogStatus('导出失败，请重试');

  }

}



async function importLogFile(file) {

  if (!file) return;

  try {

    const text = normalizeLogText(await file.text());

    await idbSet(LOG_CONTENT_KEY, text);

    logText.value = extractPageLog(text, index + 1);

    setLogStatus('已从文件导入；之后仍会自动保存在浏览器内');

  } catch (_) {

    setLogStatus('导入失败，请确认是 class-log.txt');

  }

}



function show(i) {

  if (logText && logDialog?.open) void persistCurrentPage();

  index = Math.max(0, Math.min(slides.length - 1, i));

  slides.forEach((s, j) => { s.hidden = j !== index; });

  document.querySelector('#position').textContent = `${index + 1} / ${slides.length}`;

  prev.disabled = index === 0;

  next.disabled = index === slides.length - 1;

  history.replaceState(null, '', `#${index + 1}`);

  window.scrollTo(0, 0);

  if (logPage) logPage.textContent = index + 1;

  if (logDialog?.open) void loadPageLog();

}



prev.onclick = () => show(index - 1);

next.onclick = () => show(index + 1);



document.querySelector('#notes').onclick = function notesToggle() {

  notes = !notes;

  document.querySelectorAll('.notes').forEach((n) => { n.hidden = !notes; });

  this.setAttribute('aria-pressed', String(notes));

  this.textContent = notes ? '隐藏备注' : '教师备注';

};



document.querySelector('#classlog-open').onclick = async () => {

  if (logPage) logPage.textContent = index + 1;

  logDialog.showModal();

  await loadPageLog();

};



logText?.addEventListener('input', () => schedulePersistCurrentPage());



document.querySelector('#classlog-export')?.addEventListener('click', (e) => {

  e.preventDefault();

  void exportLogFile();

});



document.querySelector('#classlog-import')?.addEventListener('click', (e) => {

  e.preventDefault();

  document.querySelector('#classlog-import-file')?.click();

});



document.querySelector('#classlog-import-file')?.addEventListener('change', (e) => {

  const file = e.target.files?.[0];

  void importLogFile(file);

  e.target.value = '';

});



logDialog?.addEventListener('close', () => {

  void persistCurrentPage();

});



document.querySelector('#all').onclick = function allToggle() {

  all = !all;

  document.body.classList.toggle('all', all);

  this.textContent = all ? '逐页模式' : '连续阅读';

  this.setAttribute('aria-pressed', String(all));

};



document.querySelector('#print').onclick = () => window.print();



document.addEventListener('keydown', (e) => {

  if (['BUTTON', 'A', 'SUMMARY', 'INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

  if (['ArrowRight', 'PageDown', ' '].includes(e.key)) {

    e.preventDefault();

    show(index + 1);

  }

  if (['ArrowLeft', 'PageUp'].includes(e.key)) {

    e.preventDefault();

    show(index - 1);

  }

  if (e.key === 'Home') show(0);

  if (e.key === 'End') show(slides.length - 1);

});



function showAnchor(hash) {
  const name = decodeURIComponent((hash || '').slice(1));
  if (!name) { show(0); return; }
  if (/^\d+$/.test(name)) { show(parseInt(name, 10) - 1); return; }
  const el = document.getElementById(name);
  const slide = el ? el.closest('.slide') : null;
  if (slide) {
    show(slides.indexOf(slide));
    history.replaceState(null, '', `#${name}`);
    if (all && el.scrollIntoView) el.scrollIntoView({ block: 'center' });
  } else {
    show(0);
  }
}
showAnchor(location.hash);
window.addEventListener('hashchange', () => showAnchor(location.hash));



document.querySelectorAll('.body a[href]').forEach((a) => {

  const h = a.getAttribute('href');

  if (h.includes('notebook') || h.includes('localhost:8888')) {

    a.target = '_blank';

    a.rel = 'noopener';

  }

});


