# Phase 3 — Persian UI (RTL + Vazirmatn + 7 poets)

Copy the `philoagents-ui/` folder in this zip over your repo's `philoagents-ui/` folder (overwrite when asked), then rebuild the UI container.

## Files changed (9)

| File | What changed |
|---|---|
| `index.html` | `lang="fa"`, Vazirmatn font from jsDelivr CDN, Persian title «شاعران پارسی» |
| `public/style.css` | New `#dialogue-panel` DOM overlay styles: RTL, Vazirmatn, dark panel, styled input |
| `src/main.js` | Waits for Vazirmatn to load before starting Phaser (avoids wrong-font first render) |
| `src/classes/DialogueBox.js` | **Rewritten as a DOM overlay** (div + real HTML `<input dir="rtl">`) instead of canvas text — proper Persian shaping, RTL, native typing/IME |
| `src/classes/DialogueManager.js` | **Rewritten**: no more per-key capture; the HTML input owns typing. Enter sends, ESC closes. WebSocket streaming + HTTP fallback kept identical |
| `src/scenes/Game.js` | 10 philosophers + Miguel/Paul → **7 poets** (`saadi`, `hafez`, `molavi`, `saeb`, `bidel`, `iqbal`, `rahi`) with Persian name labels. SPACE opens dialogue; keyboard is handed to the input while talking |
| `src/classes/Character.js` | New `spriteId` concept: backend `id` (poet) is decoupled from the sprite atlas it reuses. Name label uses Vazirmatn |
| `src/scenes/MainMenu.js` | Persian buttons (شروع بازی / راهنما / صفحهٔ پروژه → your fork), Persian instructions, Vazirmatn |
| `src/scenes/PauseMenu.js` | Persian labels (بازی متوقف شد / ادامهٔ بازی / منوی اصلی / شروع دوباره), Vazirmatn |

NOT changed: `Preloader.js`, tilemap JSON, sprites, `services/*` (API URLs are Phase 5).

## Poet → sprite → spawn mapping

Until custom sprites are drawn, each poet reuses an existing character atlas and spawn point (the Tiled map is untouched):

| Poet id | Label | Reused sprite | Spawn object |
|---|---|---|---|
| `saadi` | سعدی | socrates | Socrates |
| `hafez` | حافظ | plato | Plato |
| `molavi` | مولوی | aristotle | Aristotle |
| `saeb` | صائب تبریزی | descartes | Descartes |
| `bidel` | بیدل دهلوی | leibniz | Leibniz |
| `iqbal` | اقبال لاهوری | turing | Turing |
| `rahi` | رهی معیری | dennett | Dennett |

(Miguel and Paul NPCs were removed.)

## How dialogue works now

1. Walk up to a poet and press **SPACE** → the RTL dialogue panel opens and the HTML input is focused. Phaser keyboard input is disabled while the panel is open (so arrows/SPACE don't move the player).
2. Type Persian in the input (native browser typing — no more canvas key capture), press **Enter** to send.
3. The reply streams into the panel via the existing WebSocket, right-to-left in Vazirmatn.
4. Press **Enter** again to ask more, or **ESC** to close (keyboard is returned to the game).

## Run & test (Git Bash)

```bash
cd /d/WorkspaceNew/Linkdin/aitown/PersianPoetAgents
# copy the philoagents-ui folder from the zip over the repo, then:
docker compose up -d --build ui
```

Open http://localhost:8080 and check:

- [ ] Main menu is Persian in Vazirmatn (شروع بازی / راهنما / صفحهٔ پروژه)
- [ ] 7 NPCs roam with Persian name labels (سعدی، حافظ، مولوی، صائب تبریزی، بیدل دهلوی، اقبال لاهوری، رهی معیری)
- [ ] SPACE near حافظ opens the RTL panel with his name in the header
- [ ] Persian typing works directly in the input; Enter sends
- [ ] Reply streams right-to-left in Vazirmatn
- [ ] ESC closes the dialogue and you can walk again; ESC elsewhere opens the (Persian) pause menu

## Notes

- The font loads from jsDelivr CDN. For fully-offline builds, download `Vazirmatn` woff2 files into `public/fonts/` and swap the `<link>` in `index.html` for local `@font-face` rules in `style.css` — we can do that in Phase 5 for GitHub Pages if you prefer.
- Poet replies with mixed Persian/Latin text render fine because the panel is DOM, not canvas (`direction: rtl` handles bidi).
- Custom poet sprites remain an optional Phase 3 task — the `spriteId` field means dropping new atlases in later only requires changing one word per poet in `Game.js`.
