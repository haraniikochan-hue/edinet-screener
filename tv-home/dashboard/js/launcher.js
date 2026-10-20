const brands = new Map([
  ['smarttube', 'smarttube'], ['smarttubenext', 'smarttube'],
  // The parents' TV runs YouTube itself: the same artwork, launching YouTube.
  ['youtube', 'smarttube'],
  ['unext', 'unext'], ['ユーネクスト', 'unext'],
  ['netflix', 'netflix'], ['ネットフリックス', 'netflix'],
  ['primevideo', 'prime'], ['amazonprimevideo', 'prime'], ['プライムビデオ', 'prime'],
  ['disney+', 'disneyplus'], ['disneyplus', 'disneyplus'], ['ディズニープラス', 'disneyplus'],
  ['spotify', 'spotify'], ['spotifymusic', 'spotify'], ['スポティファイ', 'spotify'],
  ['playストア', 'playstore'], ['googleplayストア', 'playstore'], ['playstore', 'playstore'], ['googleplaystore', 'playstore'],
]);

// Only the supplied Android package is used to launch; the display name selects artwork.
// The app's own icon comes from the launcher as a PNG or WebP data URL; nothing else is accepted as an image source.
const appIcon = icon => typeof icon === 'string' && /^data:image\/(?:png|webp);base64,[A-Za-z0-9+/=]+$/.test(icon) ? icon : '';
export function nativeAppTile({name, packageName, icon: iconData}) {
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'app-tile';
  button.dataset.package = packageName; button.setAttribute('aria-label', name);
  const brand = brands.get(name.normalize('NFKC').toLowerCase().replace(/[\s\-・]/g, '')) || 'generic';
  button.dataset.brand = brand;
  const icon = document.createElement('span'); icon.className = 'app-icon'; icon.setAttribute('aria-hidden', 'true');
  if (brand === 'unext' || brand === 'disneyplus') {
    const image = document.createElement('img'); image.src = `assets/apps/${brand}.png`; image.alt = '';
    icon.append(image);
  } else if (brand === 'playstore') {
    // The full-colour Google Play mark on white, as on phones; the TV's own icon is dark and edge to edge.
    const image = document.createElement('img'); image.src = 'assets/apps/google-play.svg'; image.alt = ''; image.className = 'app-logo';
    icon.append(image);
  } else if (brand !== 'generic') {
    const mark = document.createElement('span'); mark.className = 'app-brand-mark'; icon.append(mark);
  } else if (appIcon(iconData)) {
    const image = document.createElement('img'); image.src = appIcon(iconData); image.alt = '';
    icon.append(image); button.dataset.art = 'app';
  } else {
    icon.textContent = [...name].slice(0, 2).join('');
  }
  const label = document.createElement('span'); label.className = 'app-label'; label.textContent = name; label.setAttribute('aria-hidden', 'true');
  button.append(icon, label);
  return button;
}

export function pressApp(button) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const icon = button.querySelector('.app-icon');
  if (!icon?.animate) return;
  for (const animation of icon.getAnimations()) animation.cancel();
  icon.animate([
    {transform:'translateY(-8px) scale(1.14)'},
    {transform:'translateY(-3px) scale(1.02)', offset:.35},
    {transform:'translateY(-8px) scale(1.14)'},
  ], {duration:420, easing:'cubic-bezier(.25,1.25,.4,1)'});
}
