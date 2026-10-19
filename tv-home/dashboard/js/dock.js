// The TV app's dock: which installed apps it shows and in what order. The user reorders apps and
// takes them off the dock from the long-press menu; nothing is uninstalled. Preferences are a plain
// {order:[package…], hidden:[package…]} kept in localStorage, so apps installed later simply join the end.
export const DOCK_KEY = 'tv-home-dock';
const PACKAGE = /^[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+$/;

export function normalizeDock(input) {
  const list = value => Array.isArray(value) ? [...new Set(value.filter(p => typeof p === 'string' && PACKAGE.test(p)))] : [];
  return { order:list(input?.order), hidden:list(input?.hidden) };
}

// apps: [{name, packageName, …}] in the launcher's default order (the pinned dock first).
export function arrangeDock(apps, prefs) {
  const { order, hidden } = normalizeDock(prefs);
  const byPackage = new Map(apps.map(app => [app.packageName, app]));
  const known = order.filter(p => byPackage.has(p));
  const sequence = [...known, ...apps.map(app => app.packageName).filter(p => !known.includes(p))];
  const away = new Set(hidden);
  return {
    dock:sequence.filter(p => !away.has(p)).map(p => byPackage.get(p)),
    all:[...apps].sort((a, b) => a.name.localeCompare(b.name, 'ja')),
  };
}

// Moves one dock app a step left (-1) or right (+1); dockPackages is the dock as shown.
export function moveInDock(prefs, dockPackages, packageName, step) {
  const { order, hidden } = normalizeDock(prefs);
  const dock = [...dockPackages], from = dock.indexOf(packageName), to = from + step;
  if (from < 0 || to < 0 || to >= dock.length) return { order, hidden };
  [dock[from], dock[to]] = [dock[to], dock[from]];
  return { order:[...dock, ...order.filter(p => !dock.includes(p))], hidden };
}

export function setOnDock(prefs, packageName, onDock) {
  const { order, hidden } = normalizeDock(prefs);
  return { order, hidden:onDock ? hidden.filter(p => p !== packageName) : [...new Set([...hidden, packageName])] };
}
