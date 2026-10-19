# AGENTS.md

This project builds a custom home screen (launcher) and dashboard for a Xiaomi TV (assumed Google TV / Android TV).

- Since v0.10.0 the TV's home screen is the Android app in `android/` (WebView over `dashboard/`); the stock Google TV home is disabled on the TV. See HANDOFF section 3.4, including how to undo it.
- Read **`START_HERE.md`** and **`HANDOFF.md`** (sections 1, 1.1 and 3.4 first). The current app is v0.24.4 (installed on the TV; Down from the calendar's last row goes to its page buttons, then the dock; the calendar card's later pages list eight weeks of earnings of 25 market-moving companies from Nasdaq's calendar, shown by ticker, bundled logo and each company's usual release time in Japan, HANDOFF section 1): the v0.5.5 layout with an Apple/iOS-style refresh, TV-only (one scaled 1920×1080 `#screen`, section 3.3; no phone or portrait layouts), running as the TV's home screen through the Android app in `android/`. Keep it light on a TV (section 3.1) and fully usable with a D-pad (section 3.2). The user likes Apple/iOS design and wants the UI to keep getting more refined.
- Use `dashboard/` and `artifacts/dashboard-desktop.png` as the current design baseline. `mockups/`, `references/`, and `docs/HANDOFF_HISTORY.md` are historical context.
- Preserve the accepted layout, spacing, unified market and seven-app dock unless the user requests a change. SmartTube uses YouTube artwork only; its launch target remains SmartTube.
- Settled preferences and open items are distinguished in `HANDOFF.md`. Ask only for missing information needed for the next requested action; do not repeat answered setup questions.
- Edit `dashboard/`; the Android build copies it into the APK (`dist/` is only for static hosting, regenerate it with `npm run build`). Build the APK in `android/` and install it with `adb install -r` (HANDOFF section 1.1).
- Commit and push to branch `ccr-123aaf7c-88ru7c` without asking (the user's instruction); open a pull request only when asked.
- The user is often using the TV: do not inject remote keys with `adb shell input`; check the page through a debug build's DevTools and ask the user to try remote actions.
- Record verification scope accurately: real public feeds, controlled fixtures, and unverified accounts/TV hardware are different.
- Never commit API keys.
- Confirm with the user before running any command that disables system apps on the TV; see `HANDOFF.md` for the protected components. The handoff request does not authorize TV changes or deployment.
