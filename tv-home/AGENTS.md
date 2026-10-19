# AGENTS.md

This project builds a custom home screen (launcher) and dashboard for a Xiaomi TV (assumed Google TV / Android TV).

- Read **`START_HERE.md`** and **`HANDOFF.md`** first. The current app is v0.6.0: a design refresh of the v0.5.5 layout. The user likes Apple/iOS design and wants the UI to keep getting more refined.
- Use `dashboard/` and `artifacts/dashboard-desktop.png` as the current design baseline. `mockups/`, `references/`, and `docs/HANDOFF_HISTORY.md` are historical context.
- Preserve the accepted layout, spacing, unified market and seven-app dock unless the user requests a change. SmartTube uses YouTube artwork only; its launch target remains SmartTube.
- Settled preferences and open items are distinguished in `HANDOFF.md`. Ask only for missing information needed for the next requested action; do not repeat answered setup questions.
- Edit `dashboard/`, then regenerate `dist/` with `npm run build`. Do not maintain separate changes in `dist/`.
- Record verification scope accurately: real public feeds, controlled fixtures, and unverified accounts/TV hardware are different.
- Never commit API keys.
- Confirm with the user before running any command that disables system apps on the TV; see `HANDOFF.md` for the protected components. The handoff request does not authorize TV changes or deployment.
