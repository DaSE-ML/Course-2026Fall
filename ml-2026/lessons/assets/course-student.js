const slides = [...document.querySelectorAll('.slide')];
let index = 0;
let all = false;
const prev = document.querySelector('#prev');
const next = document.querySelector('#next');

function show(i) {
  index = Math.max(0, Math.min(slides.length - 1, i));
  slides.forEach((s, j) => { s.hidden = j !== index; });
  document.querySelector('#position').textContent = `${index + 1} / ${slides.length}`;
  prev.disabled = index === 0;
  next.disabled = index === slides.length - 1;
  history.replaceState(null, '', `#${index + 1}`);
  window.scrollTo(0, 0);
}

prev.onclick = () => show(index - 1);
next.onclick = () => show(index + 1);

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
