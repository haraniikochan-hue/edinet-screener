// Pre-blurred "glass" for the TV stage. A live backdrop-filter re-blurs every
// card whenever anything behind or inside it changes, which a TV GPU cannot
// sustain. Instead each background photo is blurred once into a small canvas
// that sits under the cards, clipped to their rounded rectangles.
const WIDTH = 480;
// ≈ blur(24px) at the stage's 1920px, measured on a 480px-wide canvas.
const FILTER = 'blur(6px) saturate(1.5)';
// Two materials, one per theme (js/daypart.js themeFor).
// Dark: the glass holds back highlights: brightness above KNEE (sRGB luma, 0–255) rolls off smoothly
// towards CAP, scaling red, green and blue together so the photo keeps its colours. A bright sky becomes
// dim, tinted glass under white text; a night photo, mostly below the knee, stays clear.
const KNEE = 34, CAP = 60;
// Light: the photo is lifted towards white — every channel moves into LIGHT_FLOOR–255 — so dark buildings
// and bright sky alike become a pale glass that keeps the photo's tint, under dark text (iOS light mode).
const LIGHT_FLOOR = 160, LIGHT_SPAN = .36;
// Used instead when the photo cannot be read (a host without CORS): a flat ceiling or floor, which greys colours.
const CEILING = 'rgb(70,74,84)', FLOOR = 'rgb(196,198,204)';

export const frostSupported = () => typeof CSS !== 'undefined' && CSS.supports('clip-path','path("M0 0H1V1Z")')
  && Boolean(document.createElement('canvas').getContext);

// Rounded rectangles in viewport pixels, one sub-path per card.
export function roundedRectsPath(rects, radius) {
  const n = v => Math.round(v * 10) / 10;
  return rects.map(({x,y,width:w,height:h}) => {
    const r = Math.min(radius, w / 2, h / 2);
    return `M${n(x+r)} ${n(y)}H${n(x+w-r)}A${n(r)} ${n(r)} 0 0 1 ${n(x+w)} ${n(y+r)}V${n(y+h-r)}A${n(r)} ${n(r)} 0 0 1 ${n(x+w-r)} ${n(y+h)}H${n(x+r)}A${n(r)} ${n(r)} 0 0 1 ${n(x)} ${n(y+h-r)}V${n(y+r)}A${n(r)} ${n(r)} 0 0 1 ${n(x+r)} ${n(y)}Z`;
  }).join('');
}

// Where a rectangle of the 1920×1080 stage falls on the photo, in fractions of the image. The photo
// covers a box 4% larger than the screen, centred horizontally and at 48% vertically (.photo-layer).
export function photoRegion({x,y,width,height}, imageAspect, screenAspect = 16 / 9) {
  const box = v => (v + .02) / 1.04;
  let x0 = box(x / 1920), x1 = box((x + width) / 1920), y0 = box(y / 1080), y1 = box((y + height) / 1080);
  if (imageAspect > screenAspect) { const w = screenAspect / imageAspect, off = (1 - w) / 2; [x0, x1] = [off + x0 * w, off + x1 * w]; }
  else { const h = imageAspect / screenAspect, off = (1 - h) * .48; [y0, y1] = [off + y0 * h, off + y1 * h]; }
  return { x0, y0, x1, y1 };
}

// Opacity of the soft shade behind text that sits on the bare photo (clock, photo credit): none while
// the photo there is dark enough for white text, and on a bright sky just enough to bring its bright
// end (p90 relative luminance) down to `target`, at most .55.
export function shadeFor(luminance, target = .1) {
  if (!(luminance > target)) return 0;
  return Math.min(.55, 1 - (target / luminance) ** (1 / 2.2));
}

// The relative luminance (WCAG) that a share (90% by default) of a region of a painted canvas stays under.
function regionLuminance(context, canvas, region, share = .9) {
  const x = Math.floor(region.x0 * canvas.width), y = Math.floor(region.y0 * canvas.height);
  const w = Math.max(1, Math.ceil(region.x1 * canvas.width) - x), h = Math.max(1, Math.ceil(region.y1 * canvas.height) - y);
  const data = context.getImageData(x, y, w, h).data, lin = v => (v /= 255) <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4, values = [];
  for (let i = 0; i < data.length; i += 4) values.push(.2126 * lin(data[i]) + .7152 * lin(data[i + 1]) + .0722 * lin(data[i + 2]));
  values.sort((a, b) => a - b);
  return values[Math.floor(values.length * share)];
}
const WHOLE = { x:0, y:0, width:1920, height:1080 };

// Whether a photo looks like its time of day, from its median brightness: a search for daytime photos
// sometimes returns a night shot and the reverse. Sunset photos may be either.
export const looksLike = (period, median) => !Number.isFinite(median) || period === 'dusk'
  || (period === 'day' ? median >= .08 : median <= .2);
// The text on the bare photo, in stage pixels.
const TEXT_ON_PHOTO = { clock: { x:216, y:96, width:500, height:160 }, caption: { x:1040, y:40, width:600, height:44 } };

function tone(context, width, height, theme) {
  const image = context.getImageData(0, 0, width, height), d = image.data, span = CAP - KNEE;
  for (let i = 0; i < d.length; i += 4) {
    if (theme === 'light') {
      d[i] = LIGHT_FLOOR + d[i] * LIGHT_SPAN; d[i + 1] = LIGHT_FLOOR + d[i + 1] * LIGHT_SPAN; d[i + 2] = LIGHT_FLOOR + d[i + 2] * LIGHT_SPAN;
      continue;
    }
    const luma = .2126 * d[i] + .7152 * d[i + 1] + .0722 * d[i + 2];
    if (luma <= KNEE) continue;
    const scale = (KNEE + span * (1 - Math.exp((KNEE - luma) / span))) / luma;
    d[i] *= scale; d[i + 1] *= scale; d[i + 2] *= scale;
  }
  context.putImageData(image, 0, 0);
}

// Draws a blurred, saturated copy of an already loaded image in the theme's material, and returns how
// strong a shadow the white text on the bare photo needs ({clock, caption}, see shadeFor) with the photo's
// median brightness (scene), or null when the photo cannot be read.
export function paintFrost(canvas, image, theme = 'dark') {
  const width = WIDTH, height = Math.max(1, Math.round(WIDTH * (image.naturalHeight || 1) / (image.naturalWidth || 1)));
  canvas.width = width; canvas.height = height;
  const context = canvas.getContext('2d');
  context.drawImage(image,0,0,width,height);
  if ('filter' in context) {
    // The sharp base only shows through the blur's transparent fringe, which
    // falls in the photo's off-screen bleed.
    context.filter = FILTER; context.drawImage(image,0,0,width,height); context.filter = 'none';
  } else {
    // Without canvas filters, a tiny resample stretched back up is a soft blur.
    const small = document.createElement('canvas'); small.width = 48; small.height = Math.max(1, Math.round(48 * height / width));
    small.getContext('2d').drawImage(image,0,0,small.width,small.height);
    context.imageSmoothingQuality = 'high'; context.drawImage(small,0,0,width,height);
  }
  try {
    // Measured on the blur before toning: the text sits on the photo as it is.
    const shade = { scene:regionLuminance(context, canvas, photoRegion(WHOLE, width / height), .5) };
    for (const [name, rect] of Object.entries(TEXT_ON_PHOTO)) shade[name] = shadeFor(regionLuminance(context, canvas, photoRegion(rect, width / height)));
    tone(context, width, height, theme);
    return shade;
  } catch {
    context.globalCompositeOperation = theme === 'light' ? 'lighten' : 'darken';
    context.fillStyle = theme === 'light' ? FLOOR : CEILING; context.fillRect(0,0,width,height);
    context.globalCompositeOperation = 'source-over';
    return null;
  }
}

export class Frost {
  constructor(container, canvases) {
    Object.assign(this,{container,canvases,ready:false,shades:[]});
  }
  paint(index, image, theme) {
    try { this.shades[index] = paintFrost(this.canvases[index], image, theme); return true; } catch { return false; }
  }
  // The painted photo's median brightness, or NaN when it could not be measured.
  scene(index) { return this.shades[index]?.scene ?? NaN; }
  // Shows a painted photo and sets the shadow strength for the clock and the photo credit
  // (--clock-shade, --caption-shade; without a measurement the stylesheet's defaults apply).
  activate(index) {
    this.canvases.forEach((canvas,i) => canvas.classList.toggle('is-active', i === index));
    const shade = this.shades[index], style = document.documentElement.style;
    for (const name of Object.keys(TEXT_ON_PHOTO)) {
      if (shade) style.setProperty(`--${name}-shade`, shade[name].toFixed(2)); else style.removeProperty(`--${name}-shade`);
    }
    this.ready = true;
  }
  clip(cards, radius) {
    const rects = cards.map(card => card.getBoundingClientRect()).filter(rect => rect.width && rect.height);
    this.container.style.clipPath = rects.length ? `path('${roundedRectsPath(rects,radius)}')` : 'inset(50%)';
  }
}
