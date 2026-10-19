const candidates = root => [...root.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),summary,[tabindex="0"]')].filter(el => !el.closest('[hidden]') && el.getClientRects().length && el.tabIndex >= 0);
export function directionalTarget(current, elements, direction) {
  const origin = current.getBoundingClientRect();
  const horizontal = direction === 'ArrowLeft' || direction === 'ArrowRight';
  const sign = direction === 'ArrowLeft' || direction === 'ArrowUp' ? -1 : 1;
  const cx = origin.left + origin.width / 2, cy = origin.top + origin.height / 2;
  const ranked = elements.filter(el => el !== current).map(el => {
    const r = el.getBoundingClientRect();
    const dx = r.left + r.width / 2 - cx, dy = r.top + r.height / 2 - cy;
    const primary = (horizontal ? dx : dy) * sign, cross = Math.abs(horizontal ? dy : dx);
    const overlaps = horizontal ? r.top < origin.bottom && r.bottom > origin.top : r.left < origin.right && r.right > origin.left;
    return { el, primary, score:primary + cross * 2 + (overlaps ? 0 : 1000) };
  }).filter(item => item.primary > 2).sort((a,b) => a.score - b.score);
  return ranked[0]?.el;
}
export function installNavigation({modal, closeModal}) {
  document.addEventListener('keydown', event => {
    const inModal = !modal.hidden;
    const root = inModal ? modal : document.querySelector('#stage');
    const elements = candidates(root);
    if (event.key === 'Escape' || event.key === 'BrowserBack') {
      if (inModal) { event.preventDefault(); closeModal(); }
      return;
    }
    if (event.key === 'Tab' && inModal) {
      const i = elements.indexOf(document.activeElement);
      if (event.shiftKey && i <= 0) { event.preventDefault(); elements.at(-1)?.focus(); }
      if (!event.shiftKey && i === elements.length - 1) { event.preventDefault(); elements[0]?.focus(); }
      return;
    }
    if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)) return;
    if (event.target.matches('select,input:not([type="checkbox"]),textarea,[contenteditable]')) return;
    const target = elements.includes(document.activeElement) ? directionalTarget(document.activeElement,elements,event.key) : elements[0];
    if (target) { event.preventDefault(); target.focus({preventScroll:true}); if (!document.body.classList.contains('tv') || inModal || target.closest('.native-apps')) target.scrollIntoView({block:'nearest',inline:'nearest',behavior:'auto'}); }
  });
}
