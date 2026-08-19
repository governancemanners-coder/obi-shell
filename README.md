# OBLITERATUS // Quasar Agent-OS — OBI

A phone-first **agent-OS** for **OBI (Obliteratus)** — Sean's reverse-engineering &
personal-security harness. Onyx-black event horizon, rotating gold accretion disk,
gravitational-lensing violet, cream/tan text, glassmorphism.

This is a **complete two-piece system**:

```
obi-shell/
├── index.html            ← the app (PWA — installs to your home screen)
├── manifest.webmanifest  ← PWA manifest
├── sw.js                 ← offline service worker
├── icon.svg              ← quasar app icon
└── bridge/
    ├── obi_bridge.py      ← the device half: serves the app + device control + real skills
    ├── install.sh         ← one-command Termux setup
    └── README.md          ← bridge docs
```

---

## Run it (full power, on your phone)

```bash
# in Termux on Android
pkg install python termux-api git
git clone <this repo> && cd AionUi/obi-shell/bridge
bash install.sh

# drop your OBI skill files where the bridge expects them
cp /path/to/obi_skill_*.py            ~/obi/skills/adversarial/
cp /path/to/obi_command_dispatcher.py ~/obi/commands/

# launch
export OBI_ALLOW_EXEC=1                 # enable device control (optional)
python obi_bridge.py                    # → http://localhost:8420
```

Open **http://localhost:8420**, **Add to Home screen**, then in the app pick
**Settings → OBI's brain → Obliteratus Bridge**. Now everything is live:
real model (via local Ollama), real `/scan` etc. through your Python skills,
device control, and screen capture.

## Or use it right now (no phone setup)

Open the app in any browser and go to **Settings → OBI's brain**:
- **OpenRouter** or **Anthropic** — paste a key, OBI thinks immediately (works in-browser).
- Or leave it unconnected — the offline scanners and voice still work.

---

## What's live

| | Works offline (no backend) | Needs a provider | Needs the bridge |
| --- | :---: | :---: | :---: |
| Quasar / event-horizon UI, glassmorphism | ✅ | | |
| Chat with OBI persona | ✅ | | |
| **Live streaming AI** (OBI's SOUL as system prompt) | | ✅ OpenRouter/Anthropic/Ollama/OpenAI-compat | ✅ local Ollama |
| Text-to-speech (play each reply) + STT dictation | ✅ | | |
| `/scan /sescan /mcpscan` (ported scanners) | ✅ | | ✅ real Python skills |
| `/se /net /ext /poi /mcp` knowledge + `/skills` `/help` | ✅ | | ✅ full dispatcher |
| Workspace: ingest, drag-drop, one-tap file injection scan | ✅ | | |
| Session history + notifications | ✅ | | |
| Agent Screen thought-stream (THINK/TOOL/OBS/ACT) | ✅ | ✅ real stream status | |
| Self-protection: input injection-scanned before OBI acts | ✅ | | |
| **proot / device control** (`/exec`) | | | ✅ |
| **Screen capture** from device | | | ✅ |
| Install to home screen (PWA), offline shell | ✅ | | |

The app degrades gracefully: no provider → offline scanners; no bridge → the app
falls back to its built-in JS scanners for slash commands.

## Security posture (built in, per OBI's SOUL)

- Your input is injection-scanned **before** OBI acts on it; flagged content is
  surfaced, not executed.
- API keys are stored only in this device's `localStorage`.
- The bridge binds to `127.0.0.1`, keeps `/exec` **off** unless `OBI_ALLOW_EXEC=1`,
  and supports an `OBI_TOKEN` shared secret.
- Tool/`/exec` output should pass `scan_tool_result()` before re-entering context —
  the ReAct-loop defense from skill 6.

## Next step: folding into AionUi proper

The prototype is deliberately standalone so it runs anywhere today. To make it a
first-class AionUi surface, port `index.html` into `packages/desktop/src/renderer`
as Arco components (follow the repo's `architecture` skill — 10-children/dir,
semantic tokens, no raw HTML), reusing AionUi's multi-provider model plumbing and
IPC bridge for the device layer in place of the standalone Termux bridge.

*v0.1 · branch `claude/obi-wrapper-agent-os-2nwxpa` · all processing local.*

---

## Live demo (stable link)

The PWA is served (no install, no dummy data) at:

**https://governancemanners-coder.github.io/obi-shell/**

Open it in a browser. For full power (real model + device skills), run the
bridge on your own device (phone/desktop) and point the app at it — OBI is a
personal, local-first tool:

```bash
cd obi-shell
OBI_ALLOW_EXEC=1 python bridge/obi_bridge.py --port 8420
# in config.js set BRIDGE_URL to http://localhost:8420 (same device)
# or http://<your-device-LAN-ip>:8420 from another device
```

### New this build: OBI Team (`/team`)
Decompose a goal across specialist agents (Agent-Zero-style): Recon, Reverser,
Red Team, Analyst, Defender, Scribe. Tap the **Team** button (or `/team <goal>`).
Runs each subagent, synthesizes a brief, and saves it to per-project memory
(`obi/projects/<project>/memory.jsonl`). Subagents run sequentially (rate-limit
safe). With no model connected it falls back to an offline heuristic — connect
Ollama or a cloud provider in Settings → OBI's brain for live analysis.

### Restart-on-boot (keep it stable)
The bridge is a long-running process. To have it auto-start in Termux, add to
your `~/.bashrc` / `~/.profile`:
```bash
pgrep -f "obi_bridge.py" >/dev/null || (cd ~/obi-shell && OBI_ALLOW_EXEC=1 nohup python bridge/obi_bridge.py --port 8420 >/dev/null 2>&1 &)
```

### Reports (this build)
- `OBI_DEV_STATE.md` — structured development state (what OBI is / is NOT, architecture, verified tests, limitations, next steps).
- `COUNCIL_OF_FORMATS.md` — UI/UX + output-format review by the Council of Formats.

*Repo: https://github.com/governancemanners-coder/obi-shell*
