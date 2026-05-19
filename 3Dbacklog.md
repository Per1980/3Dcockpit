# 3Dcockpit — Backlog & Sprint Log

Living document. Updated at the end of every session.

**Convention.** Each chat session is one sprint. Story points are
Fibonacci-ish: 1 = trivial, 2 = small, 3 = real work, 5 = significant,
8 = chunky, 13 = epic, ∞ = art project. The total at the bottom is for
curiosity, not performance review.

**Scope.** 3D depth-tiered verdict visualization. Bubble per ticker,
Z-axis = verdict severity (NOW BUY closest, NOW SELL deepest).
Cursor-as-focal-point: bubbles near the cursor sharpen; distant ones
blur and dim. Two visual axes operating at once -- tier baseline
(intrinsic, verdict-driven) plus cursor proximity (overlay, gaze-
driven). Discipline angle: green naturally lives where attention
defaults; sell signals stay visible but recessed until deliberately
pointed at.

**Hard rule.** Main cockpit codebase is read-only from this project.
Any required change in scoring.py / app.py / app_views.py / theme.py /
fetch.py / etc. gets filed as a request in the main project's BACKLOG.md,
not edited from here.


## Open Backlog

### Tier 1 -- Ship soon (~17-22 SP)

| # | Task | SP | Why this priority |
|---|------|----|-------------------|
| 1 | **Six-tier vertical ladder.** One bubble per verdict at descending Z-depth. Tier order from `scoring.VERDICT_ORDER`. Camera unchanged from current PoC. Grid kept or killed based on feel once six bubbles exist. | 2 | First proof the depth axis reads visually. |
| 2 | **Tier-driven visual taper.** Apply `theme.VERDICT_BG` colors + per-tier opacity (1.0 -> 0.3) + per-tier pixel-size taper (40 -> 18) + desaturation toward back. Decision point baked in: does fake-blur via opacity + desat sell the out-of-focus effect, or do we need real shaders? If shaders, kill the project here rather than chase scope creep. | 3 | The whole concept hinges on whether this reads. Honest gate. |
| 3 | **Path B layout: ~36 random bubbles in tiers.** Read portfolio.json (or screener.json based on a hardcoded mode for now) for tickers + names. Assign weighted-random verdict per ticker, skewed toward CAUTION to match real-world distribution. Position with deterministic md5-hash jitter so layouts are stable across runs (same trick as `AAA12_combined.py` quadrant plot). One GLTextItem label per bubble. | 2 | First time the scene looks like the portfolio instead of a demo. |
| 4 | **Camera starting pose + bounds.** Find an elevation/distance that frames all 36 bubbles without manual zoom. Set `setCameraPosition` defaults. Optionally clamp pan so accidental drag can't drift into the void. | 1-2 | Once the scene is populated, the current single-bubble camera is wrong. |
| 5 | **Cursor-distance focus overlay (screen-space).** Project bubble world positions to 2D pixels every frame, compute distance to mouse, apply Gaussian-ish falloff to size + opacity + saturation on top of the tier baseline. Wide radius (~150-200px default) so multiple bubbles can be in focus at once. Cinematic, not magnifier-narrow. | 5 | The actual feature pitch. Test: can a deliberate point at the back tier bring a sell signal forward without ambient sell signals ever stealing attention? |
| 6 | **Focus smoothing.** Per-frame lerp toward target opacity/size/saturation so the focus zone glides instead of snapping. Single damping factor exposed for tuning (~0.15 initial guess). | 1 | Without this, 36 bubbles snapping on cursor movement looks like noise rather than depth-of-field. |
| 7 | **Click -> detail panel placeholder.** Reuse the same 2D projection used for focus, plus radius hit-test. Click opens a side panel (Qt widget or overlay) with ticker, verdict, reason from analyze_stock dict. Nothing fancy. Real detail content comes later. | 2 | Original spec promised a detail view on click. Placeholder unblocks the end-to-end interaction loop. |
| 8 | **3DConnexion SpaceMouse integration.** Per owns one. pyqtgraph has no native binding; needs the 3dconnexion python SDK or raw HID. Camera fly-through (translate XY + orbit yaw) is the natural mapping. | 3 | Hardware is sitting there. Worth a focused side quest once the scene justifies free-look navigation. |

### Tier 2 -- Wait for the above to prove the concept (~15 SP)

| # | Task | SP | Why wait |
|---|------|----|----------|
| 9 | Path A switch: real cockpit data via `scoring.analyze_stock`. Import scoring/fetch/portfolio_io from cockpit folder (read-only). 16h cache TTL means this is effectively free. | 2 | Pointless to wire real data until the visual feel is locked. |
| 10 | Mode toggle: Owned / Candidates / Both. Mirror cockpit's existing mode pattern. Both-at-once would need different visual treatment (outlined vs filled?) to avoid candidate NOW BUYs competing with owned position attention. | 2 | First need a single mode to look right. |
| 11 | Sector clustering on X-axis. Tickers in same sector cluster horizontally; verdicts still stratify on Z. May or may not improve on random jitter -- eval visually once #3 is live. | 5 | Random may already be enough. Premature otherwise. |
| 12 | Cockpit integration: subprocess launcher from cockpit's `app.py` (same pattern as calibrator retrain), passing a JSON snapshot of current analyze_stock results to the 3D process via temp file. Avoids tkinter + PyQt coexistence pain entirely. | 5 | Project graduation milestone. Not before the visual is proven worth shipping. |

### Filed under "later, art project"

- **Catalyst sparkles + glow shaders.** Real-time particle effects on `catalyst=True` bubbles. Custom GLSL.
- **Animated tier transitions.** When verdict changes between renders, bubble swims forward/back along Z instead of teleporting. Discipline reinforced: you literally see capital migrating.
- **Trail history.** Each bubble leaves a fading trail showing last N verdicts. Needs stable verdict_log query API.
- **Real depth-of-field via render-to-texture.** Replaces fake-blur with actual gaussian blur compositing. Only worth it if Sprint 1 #2 fails the read-test.
- **Sonification.** SID chord per verdict tier triggered on verdict-change events. Per's wheelhouse.


## Sprint Log

### Sprint 1 -- Project init + hello world + backlog (~4 SP)

First sprint of the 3Dcockpit project. Goal was to prove the basic stack
works and capture the design before building. No real visual progress
beyond a single labeled bubble; that's deliberate.

| Item | SP |
|------|----|
| `3Dcockpit_poc.py` step 1: PyQtGraph + PyQt5 + PyOpenGL installed on Python 3.14, GLViewWidget + GLGridItem + single GLScatterPlotItem + GLTextItem rendering. Verified hardware-accelerated 3D works on the dev machine, GLTextItem available (pyqtgraph 0.14.0 OK), camera controls feel right under mouse. PyOpenGL_accelerate not required for this scale. | 2 |
| Architectural decisions captured before any visual build-out: (a) subprocess integration path when graduating to cockpit (tkinter + PyQt won't coexist cleanly in one process), (b) reuse `theme.VERDICT_BG` palette not `scoring.VERDICT_COLORS` (the dark-tuned palette is the right one), (c) fake-blur via per-tier opacity + desaturation before reaching for real shaders, (d) cursor-as-focal-point not hover-on-specific-bubble (cursor is a focus *zone* in screen space; distance falloff drives sharpness, multiple bubbles can be in focus at once), (e) screen-space 2D projection for picking over 3D raycasting at this scale. | 1 |
| Read of main cockpit source (scoring.py, app.py CockpitTab, theme.py, fetch.py, portfolio_io.py, signal_log_core.py, BACKLOG.md, indicators.py) to ground the visual mapping in real `analyze_stock` dict shape and to mirror existing sprint conventions. Identified all visual ammunition per bubble: verdict, direction, catalyst (bool), t_bull/t_bear, f_green/f_red, fund_grade, sector, last_bar_date, reason. Sprint 2+ will choose what to actually use; not everything earns a visual channel. | -- |
| GitHub repo set up at per1980/3dcockpit (separate from per1980/cockpit). `.gitignore` and README.md added. Initial commit. | 1 |

Notable observations from the source read:

- `theme.py` already has a 6-verdict palette tuned for dark backgrounds.
  No need to invent colors.
- `analyze_stock` returns a clean dict; everything the bubble visuals
  could want is in there.
- Cache TTL is 16h, so Path A data swaps (Tier 2 #9) will be effectively
  free when we get to them.
- The existing CockpitTab `_render_grid` is row-based 2D. The 3D view
  is a complementary spatial representation, not a replacement -- both
  can coexist in cockpit if integration happens.


## Stats

- **Sprints completed:** 1
- **Story points shipped:** 4
