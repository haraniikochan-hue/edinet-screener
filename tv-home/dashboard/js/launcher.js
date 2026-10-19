const brands = new Map([
  ['smarttube', 'smarttube'], ['smarttubenext', 'smarttube'],
  ['unext', 'unext'], ['ユーネクスト', 'unext'],
  ['netflix', 'netflix'], ['ネットフリックス', 'netflix'],
  ['primevideo', 'prime'], ['amazonprimevideo', 'prime'], ['プライムビデオ', 'prime'],
  ['disney+', 'disneyplus'], ['disneyplus', 'disneyplus'], ['ディズニープラス', 'disneyplus'],
  ['spotify', 'spotify'], ['spotifymusic', 'spotify'], ['スポティファイ', 'spotify'],
]);

// Only the supplied Android package is used to launch; the display name selects artwork.
export function nativeAppTile({name, packageName}) {
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'app-tile';
  button.dataset.package = packageName; button.setAttribute('aria-label', name);
  const brand = brands.get(name.normalize('NFKC').toLowerCase().replace(/[\s\-・]/g, '')) || 'generic';
  button.dataset.brand = brand;
  const icon = document.createElement('span'); icon.className = 'app-icon'; icon.setAttribute('aria-hidden', 'true');
  if (brand === 'unext' || brand === 'disneyplus') {
    const image = document.createElement('img'); image.src = `assets/apps/${brand}.png`; image.alt = '';
    icon.append(image);
  } else if (brand !== 'generic') {
    const mark = document.createElement('span'); mark.className = 'app-brand-mark'; icon.append(mark);
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
