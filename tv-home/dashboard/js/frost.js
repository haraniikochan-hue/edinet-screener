// Pre-blurred "glass" for the TV stage. A live backdrop-filter re-blurs every
// card whenever anything behind or inside it changes, which a TV GPU cannot
// sustain. Instead each background photo is blurred once into a small canvas
// that sits under the cards, clipped to their rounded rectangles.
const WIDTH = 480;
// ≈ blur(24px) at the stage's 1920px, measured on a 480px-wide canvas.
const FILTER = 'blur(6px) saturate(1.6)';

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

// Draws a blurred, saturated copy of an already loaded image. Cross-origin
// photos only taint the canvas, which is fine because pixels are never read.
export function paintFrost(canvas, image) {
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
}

export class Frost {
  constructor(container, canvases) {
    Object.assign(this,{container,canvases,ready:false});
  }
  paint(index, image) {
    try { paintFrost(this.canvases[index], image); return true; } catch { return false; }
  }
  activate(index) {
    this.canvases.forEach((canvas,i) => canvas.classList.toggle('is-active', i === index));
    this.ready = true;
  }
  clip(cards, radius) {
    const rects = cards.map(card => card.getBoundingClientRect()).filter(rect => rect.width && rect.height);
    this.container.style.clipPath = rects.length ? `path('${roundedRectsPath(rects,radius)}')` : 'inset(50%)';
  }
}
