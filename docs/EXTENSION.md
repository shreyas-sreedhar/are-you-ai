# The extension

Installing, using and developing the Chrome extension.

## Install

1. Start the backend first — the extension is useless without it:

   ```bash
   cd backend && uvicorn main:app --reload
   ```

2. Open `chrome://extensions`, turn on **Developer mode** (top right).
3. Click **Load unpacked** and choose the `extension/` folder.
4. Pin RUAI to the toolbar. Click it: the popup should say **RUAI is ready**.

If it says *not connected*, the backend is not running. If it says *partly
working*, the backend is up but `NIM_API_KEY` is unset — message checks will
still work in local-scan mode.

## Using it

**Videos.** Open any YouTube or Facebook video. A button appears in the top
right: **Is this video real?** Press it while the video is playing. RUAI
grabs four frames a quarter-second apart and answers in a few seconds. If the
video is paused it sends a single frame, which is less reliable and says so.

**Messages.** Open Messenger or Instagram. RUAI reads messages as they appear.
Anything that looks like fraud gets a calm warning above it, with **Why is
this a warning?** for the full verdict. On a *danger* verdict the message
itself is blurred until you press **Show the message** — never on a *caution*,
because hiding things on a maybe teaches people to ignore the blur.

**History.** The popup's dashboard button opens a timeline of every check.
It can be cleared from there, permanently.

## What it collects

Nothing leaves your machine. Frames and message text go to your own backend on
`localhost`, which sends them to NVIDIA NIM for analysis and writes the verdict
to a local CSV. Ordinary messages are not recorded at all — only ones RUAI
flagged as concerning.

Permissions requested, and why:

| Permission | Why |
|---|---|
| `storage` | Remembers the backend address and your two toggles. |
| `*://*.youtube.com/*`, `*://*.facebook.com/*`, `*://*.instagram.com/*` | The pages it checks. |
| `http://localhost:8000/*` | Your own backend. |

There is no `tabs` permission, no analytics and no remote code.

## Development

```
extension/
├── manifest.json            MV3
├── background.js            defaults on install, toolbar badge
├── shared/
│   ├── config.js            the RUAI namespace, settings, icons, el()
│   ├── api.js               backend calls, plain-language errors
│   └── verdict-view.js      the renderer — sheets, cards, states
├── content/
│   ├── video-check.js       launcher, frame capture, the video check
│   └── message-check.js     DOM scanning, pre-filter, inline warnings
├── popup/                   popup.html / .css / .js
├── dashboard/               dashboard.html / .css / .js
├── styles/
│   ├── tokens.css           GENERATED — see below
│   └── ruai.css             components
└── icons/                   GENERATED — see below
```

Content scripts listed together in the manifest share one global scope, so
there are no modules: everything hangs off `window.RUAI`. Load order is set by
the manifest and matters.

### Regenerating assets

Both are checked in, so this is only needed after changing the brand:

```bash
python scripts/sync_brand.py      # brand/tokens.css → extension/styles/
python scripts/sync_brand.py --check   # CI guard: fails if it has drifted
python scripts/make_icons.py      # draws the mark at 16/32/48/128
```

### After editing

Press the reload icon on the RUAI card in `chrome://extensions`, then reload
the page you are testing. Content scripts are injected at page load, so the
extension reload alone is not enough.

### Debugging

- **Page overlay** — the page's own DevTools console. RUAI logs failures with
  a `[RUAI]` prefix and stays quiet otherwise.
- **Service worker** — the *Inspect views: service worker* link on the
  extension card. It sleeps; clicking wakes it.
- **Popup** — right-click the popup and choose Inspect.

### Testing the UI without a page

The verdict renderer is plain DOM and can be exercised in isolation: load
`shared/config.js` and `shared/verdict-view.js` into any HTML file, call
`RUAI.view.showSheet(RUAI.view.verdictCard(sampleVerdict))`, and stub
`window.chrome` if the code path touches storage. That is how the component
sheet in the README was rendered.

## Known rough edges

- Facebook and Instagram regenerate their class names, so the message
  selectors need occasional maintenance.
- Instagram DMs are matched but not yet specially handled; Messenger is the
  tested path.
- Some sites serve video in a way that taints the canvas. RUAI detects this
  and says the site does not let it read the picture, rather than failing
  silently.
