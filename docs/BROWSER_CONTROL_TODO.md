# Browser-control project todo

- Version/context: browser-control CLI in `fortyguard-hackathon`; target `http://127.0.0.1:5173/` on the local Vite server.
- Reproduction: `browser-control execute --json "await page.goto('http://127.0.0.1:5173/'); return page.url()"`.
- Expected: a session-owned Chromium page opens and returns the CrewClock URL.
- Actual: `RelayLifecycle.ExtensionDisconnected` — the Browser Control extension is not connected.
- Recovery: `browser-control doctor` confirmed only the standalone extension was disconnected. The in-app Browser then completed the positive, approval, no-change, unavailable, and fresh-generalization UI paths. CrewClock browser acceptance is resolved; the standalone extension remains an unrelated local-tool setup item.

- 2026-08-28 recurrence: browser-control CLI 0.4.0, local CrewClock target `http://127.0.0.1:5174/`; `browser-control execute` again returned "extension is not connected" with zero active targets. Expected a session-owned page. The in-app Browser successfully completed the same normal UI path and captured the final fresh-future run; standalone extension recovery remains to load `extension/dist` in Chromium.
