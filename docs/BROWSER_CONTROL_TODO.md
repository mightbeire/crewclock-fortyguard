# Browser-control project todo

- Version/context: browser-control CLI in `fortyguard-hackathon`; target `http://127.0.0.1:5173/` on the local Vite server.
- Reproduction: `browser-control execute --json "await page.goto('http://127.0.0.1:5173/'); return page.url()"`.
- Expected: a session-owned Chromium page opens and returns the CrewClock URL.
- Actual: `RelayLifecycle.ExtensionDisconnected` — the Browser Control extension is not connected.
- Recovery: `browser-control doctor` confirmed only the standalone extension was disconnected. The in-app Browser then completed the positive, approval, no-change, unavailable, and fresh-generalization UI paths. CrewClock browser acceptance is resolved; the standalone extension remains an unrelated local-tool setup item.
