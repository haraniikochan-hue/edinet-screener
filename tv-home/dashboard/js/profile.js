// Which TV this page is built for. The TV app reports its build flavor ("home" for the user's own TV,
// "jikka" for their parents' TV); in a desktop browser `?profile=jikka` previews the parents' screen.
// The parents' TV shows no market, calendar or Spotify: it has continue watching and input switching instead.
const fromApp = () => {
  try { return typeof globalThis.window?.Android?.profile === 'function' ? String(globalThis.window.Android.profile()) : ''; } catch { return ''; }
};
const fromQuery = () => {
  try { return new URLSearchParams(globalThis.location?.search || '').get('profile') || ''; } catch { return ''; }
};
export const PROFILE = ['home', 'jikka'].find(name => name === (fromApp() || fromQuery())) || 'home';
export const JIKKA = PROFILE === 'jikka';
