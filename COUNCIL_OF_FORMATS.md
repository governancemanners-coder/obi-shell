# Council of Formats — Format/UX Review: OBI (Obliteratus) Agent-OS

**Reviewer:** Council of Formats subagent
**Subject:** OBI (Obliteratus) — "Quasar Agent-OS"
**Basis:** Strictly on-disk code, no feature invention:
- `/data/data/com.termux/files/home/obi-shell/index.html` (current on-disk build, 1,270 lines)
- `/data/data/com.termux/files/home/obi-shell/sw.js` (service worker)
- `/data/data/com.termux/files/home/obi-shell/manifest.webmanifest`, `icon.svg` (PWA assets, present)
- `/data/data/com.termux/files/home/obi/obi_delegate.py` (Agent-Zero-style delegation, 290 lines)
- `/data/data/com.termux/files/home/obi-shell/README.md` (claimed capabilities)

---

## 1. Executive verdict

OBI is a **visually coherent, mobile-first, genuinely installable PWA** with a distinctive
event-horizon brand and a strong, reusable *scan-result* format. Branding, glassmorphism, and
offline shell are real and well-executed.

The **agent-output conventions are inconsistent across the system**. The local `/scan` family
produces a rich, severity-coded finding card; the multi-agent **Team** delegation produces a
*raw, un-rendered markdown blob* with **un-styled agent cards** and **zero live progress**.
The delegation engine (`obi_delegate.py`) is sound in architecture but its "tool grants" are
decorative (no tool functions exist) and its synthesis brief never extracts the Risk rating the
Analyst profile promises.

**Top three format defects the Council should mandate fixes for:**
1. Agent cards (`.acard`/`.cards`/`.adot`/`.aname`/`.astat`) have **no CSS** — they render as
   unstyled text despite being a flagship feature.
2. `/team` output is dumped as **raw markdown inside a `<pre>`-like mono block** (no `mdLite`
   rendering), so `#`/`##`/`-` show literally.
3. **No progress visibility** for delegation — all agent cards say "done" because they are drawn
   only after the whole backend run finishes; the Agent Screen thought-stream is unused for teams.

---

## 2. UI/UX format quality (current app)

### 2.1 Branding — strong
- Wordmark `OBLITERATUS` (gold gradient text, `text-shadow` glow) + subword `Quasar Agent-OS · OBI`
  (`index.html` ≈304–305). Cohesive quasar/event-horizon vernacular throughout
  ("The horizon is stable.", "annihilating…", "core stable").
- Event-horizon `<canvas>` (`horizon()` ≈655–694): black-hole sphere, rotating gold accretion
  disk (doppler-brightened), violet-gold Einstein lensing ring, faint starfield. A genuine,
  on-brand signature visual — not a stock gradient.
- `theme-color`, `apple-mobile-web-app-*` meta, `manifest.webmanifest`, `icon.svg` all present.

### 2.2 Glassmorphism — consistent and pervasive
- Token `--glass: rgba(14,18,28,.62)` + `--blur:16px` applied to dock, icon buttons, chips,
  drop zone, tiles, notifications, input wrap, toggles (`index.html` ≈46, 100–104, 276–285).
- Works correctly: `#horizon` sits at `z-index:0`, `#app` at `z-index:2`, so translucent panels
  blur the live canvas behind them.
- **Caveat:** `backdrop-filter` over a continuously animating canvas is GPU-heavy on low-end
  Android/Termux devices. Mitigated by the `motion` toggle, but no reduced-quality fallback.

### 2.3 Mobile-first — good
- `viewport-fit=cover` + `env(safe-area-inset-*)` (≈5, 80). Single-column `max-width:560px`
  on phones, expanding to a `1fr 380px` desktop grid at `min-width:900px` (≈79–85).
- Thumb-friendly bottom nav dock; Agent Screen is a 64vh **bottom sheet** on mobile
  (`translateY` + backdrop) and a fixed side panel on desktop (≈181–187).
- Composer: auto-growing textarea, mic + send + team buttons.

### 2.4 Offline-capable PWA — genuinely supported (with a nuance)
- `sw.js` registers and caches the shell (`'./'`, `index.html`, `manifest.webmanifest`,
  `icon.svg`) with **network-first** strategy and an offline cache fallback (`sw.js` 1–27).
- `fetch` handler correctly excludes bridge/model paths (`/dispatch`,`/chat`,`/exec`,`/screen`,
  `/health`,`/fs`) and cross-origin — so offline = shell loads, but live intelligence needs the
  bridge/provider. This is honest degradation, not a false "works offline" claim.
- No web fonts (system `ui-monospace`/`system-ui`) → no offline font fetch failure. Good.

### 2.5 Accessibility — the weakest dimension
- **No `:focus-visible` rule** anywhere; only `:hover`/`:active` exist. Keyboard users get no
  visible focus ring on any control.
- **No `aria-live` region** on scan verdicts or notifications → screen readers do not announce
  a "CRITICAL" finding or a new notification.
- Decorative `<canvas id="horizon">` (≈296) has **no `aria-hidden="true"`**.
- Icon-only buttons `.act` (file delete / scan) and in-bubble `.speak` have only `title`, no
  `aria-label` (the nav dock buttons do have visible text labels, so they are acceptable).
- **Contrast:** `--tan-dim (#6E6754)` on `--void (#05060A)` is used for sub-words, `.desc`,
  `.sub` and is below WCAG AA (~3:1 for small text). `--tan (#A99B82)` is borderline.
- **Strength:** `prefers-reduced-motion` is honored in both CSS (≈291) and JS (`reduce` guard on
  the canvas loop) — exemplary.

---

## 3. Agent-output format conventions

### 3.1 Scan results — best-in-class, reusable
- `runScan()` (≈501–510) matches pattern corpora (injection / social-engineering / MCP) and
  sorts by `SEVORD`.
- `findingsHtml()` (≈795–801) renders a **verdict banner** (worst severity) + **action text**
  (`ACTIONS` map, ≈511) + per-finding rows: severity badge (`.sev.CRITICAL/HIGH/MEDIUM/CLEAN`,
  ≈141–145), category, description, and a **quoted matched snippet** window.
- This is the format the Council should treat as the *reference pattern* and propagate
  everywhere else.

### 3.2 SOUL system prompt — well-formed
- `OBI_SOUL` (≈563–573): quasar identity ("gargantuan, precise, annihilating"), the six
  adversarial-intelligence skills, four explicit self-protection directives (scan-before-act,
  no exfiltration, no unauthorized offense, knowledge ≠ authorization), and a terse style guide.
- Concise, role-stable, and actually injected as the `system` message in `streamChat` (≈595).

### 3.3 Multi-agent synthesis brief — structurally weak vs. the rest
- `obi_delegate._synthesize()` (≈269–280) emits flat markdown:
  `# Brief — <goal>`, `## <Agent>` per output, `## Next actions` with **three generic lines**
  (`"Connect a live model…"`, `"Project memory updated at …"`).
- Problems:
  - Despite the **Analyst** profile being instructed to assign `Risk: LOW/MED/HIGH/CRITICAL`
    (≈77–79), the orchestrator **never extracts or renders a Risk rating**.
  - The brief does **not** reuse the app's rich finding format (severity badge + snippet).
  - `teamRun()` (≈948–972) renders the brief inside
    `<div class="bubble mono" … white-space:pre-wrap>${esc(out)}</div>` — i.e. **raw,
    un-rendered markdown** (literal `#`, the `#`/`##`/`-` are visible as text). The chat's
    `mdLite()` is applied to model replies but **not** to team output.
  - **Agent cards** (`.acard`/`.cards`/`.adot`/`.aname`/`.astat`) are created in JS (≈965–968)
    but **have no CSS definitions anywhere** in the stylesheet → they appear as unstyled text.
  - Roster capitalization bug: profile id `redteam` → `"Redteam"`, but `AGENT_META` key is
    `"Red Team"` (≈955) → the Red Team card falls back to the default gold color.
  - Every card's status is hardcoded `"done"` (≈967) — there is no pending/working state because
    the cards are drawn only after the single blocking `/team` POST resolves.

### 3.4 Tool grants are decorative
- `obi_delegate.PROFILES` lists `tools:["net_scan","web_recon","filescan","shell","filesys"]`
  (≈47–103), but **no such functions are defined or invoked** in the file. `_run_subagent()`
  (≈195–207) only sends a text prompt; the tool names are merely echoed into the subagent's
  prompt. The brief therefore implies tool-derived "evidence" that was never gathered.

---

## 4. README ↔ code consistency

The README's **"What's live"** table (README ≈53–69) is **largely accurate**:
- Quasar UI/glassmorphism, chat, live streaming (SOUL), TTS/STT, `/scan` family, knowledge
  commands, workspace ingest, history/notifications, Agent Screen, self-protection, device
  control, screen capture, PWA — all match code. The graceful offline fallback is real.

Inconsistencies the Council should flag:
1. **Team/delegation is undocumented in the README** but is a prominent feature (composer
   `#team` button + `/team` command + `obi_delegate.py`). The README under-states shipped
   capability.
2. **Advertised-but-dead commands offline:** `/help` (≈913–918) lists `/net-scan`,
   `/net-monitor`, `/net-capture`, `/web-intercept`, `/web-recon`, `/web-replay`, `/filescan`,
   but with no bridge these hit the `default` branch and return *"unknown command"* (≈936–938).
   README marks device-control as "needs bridge" (correct) yet the UX still advertises them.
3. **Provider-selector mismatch:** default `S.conn.provider:'nous'` (≈558, 562) and a
   `PROVIDERS.nous` entry exist, but the `<select>` (≈370–375) offers only bridge / OpenRouter /
   Anthropic / Ollama / OpenAI-compatible — **no `nous` option**. Result: on first load the
   dropdown shows "— select provider —" while a provider is already active and invisible.
4. **Naming drift:** README calls device control `/exec`; `/help` does not list `/exec` (it lists
   the `/net-*` family). Minor.

---

## 5. Recommendations to the Council

1. **Style the agent cards.** Add CSS for `.acard`/`.cards`/`.adot`/`.aname`/`.astat` using the
   existing glass + per-agent color tokens (`AGENT_META`), so `/team` output matches the design
   system instead of rendering as naked text.
2. **Render team output with `mdLite` (or a richer renderer).** Stop dumping raw markdown in a
   `white-space:pre-wrap` mono block; format the brief like other OBI messages. Better: render
   each subagent's output as its own expandable section.
3. **Add real progress visibility.** Stream team progress (SSE/NDJSON from the bridge, or
   per-agent callbacks) and drive the Agent Screen's `THINK/TOOL/OBS/ACT` tags during a run.
   Cards should transition `pending → working → done`, and show a `2/5 agents` counter — not a
   hardcoded "done".
4. **Unify output conventions.** Have `obi_delegate._synthesize()` extract **Findings + Risk**
   (the Analyst already promises a rating) and emit the same structured shape as `findingsHtml()`,
   so Team results reuse the scan-result severity badge + snippet + verdict format.
5. **Make tool grants honest.** Either implement minimal local tool shims (e.g. `filescan` via
   `file`/`strings`, `net_scan` via `nmap`) or explicitly label the grant as model-context-only
   so the brief never implies evidence that was never collected.
6. **Fix the `Red Team` color key.** Capitalize roster ids to match `AGENT_META` (`"Red Team"`),
   or key `AGENT_META` by the raw profile id, so the Red Team card gets its intended color.
7. **Surface the `nous` provider in the selector.** Add a visible `nous` option (or rename the
   default) so the active connection is selectable and the dropdown isn't blank on first load.
8. **Gate bridge-only commands in `/help`.** When `bridgeUp` is false, hide or tag
   (`↯ needs bridge`) the `/net-*`/`/filescan` entries so users aren't sent to a dead-end
   "unknown command".
9. **Accessibility pass.** Add `:focus-visible` outlines; add `aria-live="polite"` to scan
   verdict + notification regions; set `aria-hidden="true"` on the decorative canvas; add
   `aria-label` to icon-only `.act`/`.speak` buttons; raise `--tan-dim` contrast to meet AA.
10. **Document Team in the README** and reconcile `/exec` vs `/net-*` naming, so the README
    matches shipped behavior.
11. **Give `/team` an offline story.** Unlike scans (which degrade to JS), `teamRun()` hard-fails
    when the bridge is down. Either invoke `obi_delegate`'s deterministic heuristic locally or
    clearly message the requirement (the latter already exists; consider the former).
12. **Honest status indicators.** The Agent Screen "observing" pulse and core "core stable" pulse
    are always green regardless of activity. Reflect real in-flight state (pulse only during a
    run) for truthful telemetry.

---

## Appendix — evidence index (file:line)

- Branding / canvas: `index.html` ≈304–305, 655–694, theme meta ≈6–12
- Glass tokens: `index.html` ≈46, 100–104, 276–285
- Mobile / bottom sheet: `index.html` ≈5, 79–85, 181–187
- PWA: `index.html` `serviceWorker.register` (≈1202); `sw.js` 1–27
- Accessibility gaps: no `:focus-visible`; canvas `aria-hidden` absent (≈296); `--tan-dim` (≈36);
  no `aria-live` on verdicts/notifs
- Scan format: `runScan` ≈501–510; `findingsHtml` ≈795–801; `.sev` ≈141–145; `ACTIONS` ≈511
- SOUL: `OBI_SOUL` ≈563–573
- Team wiring: `#team` button ≈328; handler ≈974; `/team` case ≈928; `teamRun` ≈948–972;
  `AGENT_META` ≈944–947 (key `"Red Team"` at 955)
- Agent-card CSS absent: only usage at ≈953/965–968; no stylesheet definition found
- Default provider `nous`: `index.html` ≈558, 562; `PROVIDERS.nous` ≈580; select options ≈370–375
- `obi_delegate.py`: `PROFILES` tools ≈47–103 (no impls); `_run_subagent` ≈195–207;
  `_synthesize` ≈269–280; `run_team` ≈225–266
- README claims: `README.md` ≈53–69 (table), ≈74–82 (security), device-control naming ≈67
