(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const pages = [...document.querySelectorAll('[data-page]')];
  const progress = document.querySelector('[data-progress]');
  const live = document.querySelector('[data-live]');
  const helpButton = document.querySelector('[data-help]');
  const helpPanel = document.querySelector('[data-help-panel]');
  const previousButton = document.querySelector('[data-prev]');
  const nextButton = document.querySelector('[data-next]');
  let index = 0;

  if (!slides.length) return;

  const byHash = () => {
    const requested = decodeURIComponent(location.hash).replace(/^#\/?/, '');
    const found = slides.findIndex((slide) => slide.id === requested);
    return found >= 0 ? found : 0;
  };

  const setHelpOpen = (open) => {
    if (!helpPanel) return;
    helpPanel.hidden = !open;
    helpButton?.setAttribute('aria-expanded', String(open));
  };

  const render = (next, updateHash = true) => {
    index = Math.max(0, Math.min(next, slides.length - 1));
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      if (active) slide.focus({ preventScroll: true });
    });
    const title = slides[index].querySelector('h1, h2')?.textContent?.trim() || '幻灯片';
    pages.forEach((page) => {
      page.textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    });
    if (progress) progress.style.width = `${((index + 1) / slides.length) * 100}%`;
    if (live) live.textContent = `第 ${index + 1} 页，共 ${slides.length} 页：${title}`;
    previousButton?.toggleAttribute('disabled', index === 0);
    nextButton?.toggleAttribute('disabled', index === slides.length - 1);
    if (updateHash) history.replaceState(null, '', `#/${slides[index].id}`);
  };

  const isEditable = (element) => element && (element.matches('input, textarea, select, [contenteditable="true"]') || element.closest('[contenteditable="true"]'));
  const move = (delta) => render(index + delta);

  document.addEventListener('keydown', (event) => {
    if (isEditable(event.target)) return;
    if (['ArrowRight', ' ', 'PageDown'].includes(event.key)) { event.preventDefault(); move(1); }
    else if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); move(-1); }
    else if (event.key === 'Home') { event.preventDefault(); render(0); }
    else if (event.key === 'End') { event.preventDefault(); render(slides.length - 1); }
    else if (event.key.toLowerCase() === 'f') { document.documentElement.requestFullscreen?.(); }
    else if (event.key === '?') { event.preventDefault(); setHelpOpen(helpPanel?.hidden); }
    else if (event.key === 'Escape') { setHelpOpen(false); }
  });

  nextButton?.addEventListener('click', () => move(1));
  previousButton?.addEventListener('click', () => move(-1));
  helpButton?.setAttribute('aria-expanded', 'false');
  helpButton?.addEventListener('click', () => setHelpOpen(helpPanel?.hidden));
  window.addEventListener('hashchange', () => render(byHash(), false));
  render(byHash(), false);
})();
