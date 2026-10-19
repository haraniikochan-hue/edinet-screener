// Remote-control (D-pad) navigation for the TV screen and its dialogs.
// On the stage, focusable elements inside a [data-nav-group] move among themselves first.
// Leaving a group follows the group's data-nav-up/down/left/right (another group's name, or
// "none"); without a rule it takes the nearest element in that direction. Coming back into the
// group you just left, in the opposite direction, returns to the element you left from, and the
// opposite arrow pressed straight after crossing into a group always undoes that move.
const FOCUSABLE = 'button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),summary,[tabindex="0"]';
const DIRECTIONS = { ArrowUp:'up', ArrowDown:'down', ArrowLeft:'left', ArrowRight:'right' };
const BACK_KEYS = ['Escape','BrowserBack','GoBack'];
const OPPOSITE = { up:'down', down:'up', left:'right', right:'left' };

// Content of a closed <details> can still report boxes; only its summary is reachable.
const insideClosedDetails = el => {
  for (let details = el.closest('details'); details; details = details.parentElement?.closest('details')) {
    if (!details.open && !(el.matches('summary') && el.parentElement === details)) return true;
  }
  return false;
};
const visible = el => el.checkVisibility ? el.checkVisibility({ visibilityProperty:true }) : getComputedStyle(el).visibility !== 'hidden';
export const candidates = root => [...root.querySelectorAll(FOCUSABLE)].filter(el => !el.closest('[hidden],[data-nav-skip]')
  && el.getClientRects().length && el.tabIndex >= 0 && !insideClosedDetails(el) && visible(el));

const center = el => { const r = el.getBoundingClientRect(); return { x:r.left + r.width / 2, y:r.top + r.height / 2, r }; };
export function directionalTarget(current, elements, direction, { crossWeight = 2, alignedFirst = true } = {}) {
  const { x:cx, y:cy, r:origin } = center(current);
  const horizontal = direction === 'ArrowLeft' || direction === 'ArrowRight' || direction === 'left' || direction === 'right';
  const sign = ['ArrowLeft','ArrowUp','left','up'].includes(direction) ? -1 : 1;
  const ranked = elements.filter(el => el !== current).map(el => {
    const r = el.getBoundingClientRect();
    const dx = r.left + r.width / 2 - cx, dy = r.top + r.height / 2 - cy;
    const primary = (horizontal ? dx : dy) * sign, cross = Math.abs(horizontal ? dy : dx);
    const overlaps = horizontal ? r.top < origin.bottom && r.bottom > origin.top : r.left < origin.right && r.right > origin.left;
    return { el, primary, score:primary + cross * crossWeight + (overlaps || !alignedFirst ? 0 : 1000) };
  }).filter(item => item.primary > 2).sort((a,b) => a.score - b.score);
  return ranked[0]?.el;
}
const nearest = (from, elements) => {
  const { x, y } = center(from);
  return elements.map(el => { const c = center(el); return { el, d:Math.hypot(c.x - x, c.y - y) }; }).sort((a,b) => a.d - b.d)[0]?.el;
};
const groupOf = el => el?.closest?.('[data-nav-group]') || null;
const isTextField = el => el.matches('input:not([type="checkbox"]):not([type="radio"]),textarea,[contenteditable="true"]');

// modals: [{element, close}] — the open one traps focus and closes on Back.
// home(): the element that holds the app dock. onEdge(current, direction) may consume a move
// (e.g. paging a list) by returning true.
export function installNavigation({ modals, home, onEdge = () => false }) {
  let lastLeft = null, lastCrossing = null;
  const remembered = new Map();
  document.addEventListener('focusin', event => {
    const group = groupOf(event.target);
    if (group) remembered.set(group, event.target);
  });
  const rememberedIn = (group, elements) => { const el = remembered.get(group); return el && elements.includes(el) ? el : null; };
  // Entering a group: back to where we left it when retracing the last move, else the given or nearest member.
  const enter = (group, from, elements, direction, preferred) => {
    const members = elements.filter(el => groupOf(el) === group);
    if (!members.length) return null;
    if (lastLeft?.group === group && lastLeft.direction === OPPOSITE[direction] && members.includes(lastLeft.element)) return lastLeft.element;
    if (preferred && members.includes(preferred)) return preferred;
    return directionalTarget(from, members, direction) || nearest(from, members);
  };
  const focusHome = () => {
    const dock = home?.();
    if (!dock) return false;
    const elements = candidates(dock), target = rememberedIn(groupOf(dock) || dock, elements) || elements[0];
    if (!target || dock.contains(document.activeElement)) return false;
    target.focus({ preventScroll:true });
    return true;
  };

  document.addEventListener('keydown', event => {
    const open = modals.find(modal => !modal.element.hidden);
    if (BACK_KEYS.includes(event.key)) {
      // Back closes a dialog; on the home screen it returns focus to the app dock.
      if (open) { event.preventDefault(); open.close(); }
      else if (focusHome()) event.preventDefault();
      return;
    }
    const root = open ? open.element : document.querySelector('#stage');
    const elements = candidates(root);
    if (event.key === 'Tab' && open) {
      const i = elements.indexOf(document.activeElement);
      if (event.shiftKey && i <= 0) { event.preventDefault(); elements.at(-1)?.focus(); }
      if (!event.shiftKey && i === elements.length - 1) { event.preventDefault(); elements[0]?.focus(); }
      return;
    }
    // A remote's OK key is Enter: make it toggle switches and activate custom buttons too.
    if (event.key === 'Enter' && event.target.matches?.('input[type="checkbox"],[role="button"]:not(button)')) {
      event.preventDefault(); event.target.click(); return;
    }
    const direction = DIRECTIONS[event.key];
    if (!direction || event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target;
    // Left/right keep moving the caret in text fields; up/down always leave them, and every
    // arrow leaves a select (OK opens its picker), so a remote can never get stuck in a form.
    if (isTextField(target) && (direction === 'left' || direction === 'right')) return;
    const current = elements.includes(document.activeElement) ? document.activeElement : null;
    let next = null;
    if (!current) next = open ? elements[0] : (home?.() && candidates(home())[0]) || elements[0];
    // Undo comes first, so a group that pages at its edge (the calendar) cannot trap a quick Up-then-Down.
    else if (!open && lastCrossing?.to === current && direction === OPPOSITE[lastCrossing.direction] && elements.includes(lastCrossing.from)) next = lastCrossing.from;
    else if (onEdge(current, direction)) { event.preventDefault(); lastCrossing = null; return; }
    else {
      const group = open ? null : groupOf(current);
      // Dialogs are vertical forms: the next control below wins even when it sits at the row's far end.
      if (!group) next = directionalTarget(current, elements, direction, open && (direction === 'up' || direction === 'down') ? { crossWeight:.15, alignedFirst:false } : undefined);
      else {
        next = directionalTarget(current, elements.filter(el => groupOf(el) === group), direction);
        if (!next) {
          const rule = group.dataset[`nav${direction[0].toUpperCase()}${direction.slice(1)}`];
          if (rule && rule !== 'none') {
            const targetGroup = root.querySelector(`[data-nav-group="${rule}"]`);
            if (targetGroup) next = enter(targetGroup, current, elements, direction);
          } else if (!rule) {
            const hit = directionalTarget(current, elements.filter(el => groupOf(el) !== group), direction);
            next = hit && groupOf(hit) ? enter(groupOf(hit), current, elements, direction, hit) : hit;
          }
          if (next) lastLeft = { group, element:current, direction };
        }
      }
    }
    // The screen itself never scrolls; only a dialog or the installed-apps row scrolls to its focus.
    event.preventDefault();
    if (!next) return;
    lastCrossing = !open && current && groupOf(next) !== groupOf(current) ? { from:current, to:next, direction } : null;
    next.focus({ preventScroll:true });
    if (open || next.closest('.native-apps')) next.scrollIntoView({ block:'nearest', inline:'nearest', behavior:'auto' });
  });
  return { focusHome };
}
