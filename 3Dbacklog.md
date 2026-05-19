# 3Dcockpit -- Backlog & Sprint Log

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

### Tier 1 -- Ship soon (~12-15 SP)

Tasks #1, #2, #3, #4 shipped in Sprint 2. New item #13 added.

| # | Task | SP | Why this priority |
|---|------|----|-------------------|
| 5 | **Cursor-distance focus overlay (screen-space).** Project bubble world positions to 2D pixels every frame, compute distance to mouse, apply Gaussian-ish falloff to size + opacity + saturation on top of the tier baseline. Wide radius (~150-200px default) so multiple bubbles can be in focus at once. Cinematic, not magnifier-narrow. | 5 | The actual feature pitch. Test: can a deliberate point at the back tier bring a sell signal forward without ambient sell signals ever stealing attention? |
| 6 | **Focus smoothing.** Per-frame lerp toward target opacity/size/saturation so the focus zone glides instead of snapping. Single damping factor exposed for tuning (~0.15 initial guess). | 1 | Without this, 36 bubbles snapping on cursor movement looks like noise rather than depth-of-field. |
| 7 | **Click -> detail panel placeholder.** Reuse the same 2D projection used for focus, plus radius hit-test. Click opens a side panel (Qt widget or overlay) with ticker, verdict, reason from analyze_stock dict. Nothing fancy. | 2 | Original spec promised a detail view on click. Placeholder unblocks the end-to-end interaction loop. |
| 8 | **3DConnexion SpaceMouse integration.** Per owns one. pyqtgraph has no native binding; needs the 3dconnexion python SDK or raw HID. Camera fly-through (translate XY + orbit yaw) is the natural mapping. | 3 | Hardware is sitting there. Worth a focused side quest once the scene justifies free-look navigation. |
| 13 | **Back-face culling on sphere meshes.** Sphere geometry shows triangulated back-face wireframe pattern through the translucent front from certain angles (seen during Sprint 2 free-orbit testing). Fix: add GL_CULL_FACE to GLMeshItem glOptions; bump mesh density from rows=10 cols=18 to rows=20 cols=30 for smoother silhouettes. Probably ride in with Sprint 3 cursor-focus work. | 1 | Cosmetic but visible. Cheap fix. |

### Tier 2 -- Wait for the above to prove the concept (~15 SP)

| # | Task | SP | Why wait |
|---|------|----|----------|
| 9  | Path A switch: real cockpit data via `scoring.analyze_stock`. Import scoring/fetch/portfolio_io from cockpit folder (read-only). 16h cache TTL means this is effectively free. | 2 | Pointless to wire real data until the visual feel is locked. |
| 10 | Mode toggle: Owned / Candidates / Both. Mirror cockpit's existing mode pattern. Both-at-once would need different visual treatment (outlined vs filled?) to avoid candidate NOW BUYs competing with owned position attention. | 2 | First need a single mode to look right. |
| 11 | Sector clustering on X-axis. Tickers in same sector cluster horizontally; verdicts still stratify on Z. May or may not improve on random jitter -- eval visually once #3 is live. | 5 | Random may already be enough. Premature otherwise. |
| 12 | Cockpit integration: subprocess launcher from cockpit's `app.py` (same pattern as calibrator retrain), passing a JSON snapshot of current analyze_stock results to the 3D process via temp file. Avoids tkinter + PyQt coexistence pain entirely. | 5 | Project graduation milestone. Not before the visual is proven worth shipping. |

### Filed under "later, art project"

- **Catalyst sparkles + glow shaders.** Real-time particle effects on `catalyst=True` bubbles. Custom GLSL.
- **Animated tier transitions.** When verdict changes between renders, bubble swims forward/back along Z instead of teleporting. Discipline reinforced: you literally see capital migrating.
- **Verdict-history trails.** Each bubble leaves a fading trail showing last N verdicts (historical signal, not motion trails). Needs stable verdict_log query API.
- **Real depth-of-field via render-to-texture.** Replaces fake-blur with actual gaussian blur compositing.
- **Sonification.** SID chord per verdict tier triggered on verdict-change events. Per's wheelhouse.
- **ESP32 satellite displays.** Pinned-ticker side screens on T-Display Lilygo S3 boards over WiFi. Main scene "throws" a bubble; it leaves the 3D view with an animation; pops up on a physical screen showing that ticker's verdict + tech rows + ML score, cycling Fundamentals / Technicals / ML on a button. Long-press releases the ticker back to the main scene. JSON over MQTT or tiny HTTP. ESP-side render with LovyanGFX; matching Lissajous bubble on the small screen for visual continuity. Pure theatre but the good kind.
- **Web / Pi port.** If the main cockpit eventually moves to a browser, the 3D layer probably gets rewritten in three.js or regl. Or stays Qt and ships on a Pi 5 with a touchscreen. Touch interaction redesigns "cursor-as-focal-point" into "tap-to-pull-forward" / flick-to-throw. Decided in Sprint 2 not to over-invest in PyQt-specific polish that wouldn't port; the fake-blur-via-opacity choice ages well on weaker hardware regardless.
- **Idle screensaver mode.** Input-timeout cascade: active (you're driving the camera) -> ambient sway only; idle short (~5s after last input) -> slow auto-orbit kicks in; idle long (~30s+) -> planetary mode where tier positions become orbital paths (NOW BUY tight/fast, NOW SELL barely drifts), bubble trails, bloom, random warp-zooms through the scene, occasional catalyst sparks. SID arpeggio underneath if audio is wired. First user input snaps back to active mode instantly, no fade. Sub-features (trails / bloom / warp / sparks / audio) only make sense together as a system; building any one in isolation is wasted effort. Net effect: tool when you're using it, demoscene piece when you're not.


## Sprint Log

### Sprint 2 -- Tier ladder, taper, sway, real spheres, free orbit, NOW BUY sprinkle (~16 SP)

All four originally-scoped Tier 1 items shipped. Three live iterations
within the session: v1 baseline rendered tiers, Per pushed back on flat
look and locked-axis labels; v2 added sway + lost labels; v3 graduated
to real geometry + free orbit + front-tier emphasis. Bigger than the
backlog estimate (6-8 SP) because the scope add was the right call --
v1 by itself wouldn't have proven the concept.

| Item | SP |
|------|----|
| **#1** Six-tier vertical ladder. NOW BUY at Y=+10, NOW SELL at Y=-10, four tiers stratified in between. Verdict order from `scoring.VERDICT_ORDER`. | 2 |
| **#2** Per-tier visual taper. `TIER_TAPER` dict drives size, opacity, desaturation toward neutral grey. Front sharp/vivid; back small/dim/washed. | 3 |
| **#3** Path B layout. Reads `../portfolio.json`, assigns weighted-random verdicts (skewed toward CAUTION to match reality), positions with deterministic md5-hash jitter so layouts stay stable across runs. Same hash trick used by AAA12_combined.py quadrant plot in the main cockpit. | 2 |
| **#4** Camera pose: distance=44, elevation=10, azimuth=90. Frames the populated scene without manual zoom. | 1 |
| **Scope add: ambient sway.** Per noted depth was only readable while orbiting the camera. Each bubble now traces a small Lissajous figure with deterministic per-ticker phase + frequency. Amplitude scales by tier (front big, back nearly still) so motion parallax IS the depth cue. Tier base frequency also varies: NOW BUY breathes fast, NOW SELL nearly frozen. Side effect: encodes emotional state through motion -- buy side feels alive, sell side feels dead. | 3 |
| **Scope add: real 3D sphere meshes.** Per noted bubbles still looked flat. Replaced GLScatterPlotItem flat sprites with GLMeshItem spheres using the 'balloon' shader. Real geometry, real shading. Each bubble = main sphere + larger soft-glow shell. MeshData is shared per tier (one main + one glow mesh per tier; 36 GLMeshItems reference them by Python ref). | 3 |
| **Scope add: free-orbit camera.** GLViewWidget hard-clamps elevation to ±90° in its `orbit()` method. Subclassed as `FreeOrbitView` and replaced the clamp with modulo wrap to [-180, 180]. Full tumble enabled. | 1 |
| **Scope add: NOW BUY sprinkle.** Front-tier bubbles get a wider glow shell (3x radius vs 1.3-1.5x for back tiers) plus a slow size pulse (±10% at 0.55 Hz). GET READY and WARMING pulse gentler; CAUTION and below stay static. Reinforces the "alive vs dead" feel from the sway frequencies. | 1 |
| **Removed: tier-name labels.** Floating "NOW BUY" / "GET READY" / etc. text at each Y depth in v1. Per killed them: locked the scene to one viewing axis (text is camera-facing so they read backwards from behind), and verdict colors already encode tier identity. Net negative once free orbit was on the table. | -- |
| theme.VERDICT_BG + BG imported read-only from `../theme.py`. First confirmation that the parent-folder import architecture works clean. The "no editing main cockpit files" rule held the whole sprint. | -- |

Notable findings worth carrying forward:

- **Back-face culling not enabled by default** on GLMeshItem. From certain
  angles the triangulated back-face geometry shows through the translucent
  front. Filed as Tier 1 #13.
- **'balloon' shader takes a uniform `color=` kwarg**, not per-vertex
  colors. Trying to `setVertexColors` on a balloon-shaded mesh is wasted.
- **GLViewWidget elevation clamp** is a hard literal in `orbit()` -- easy
  override, but worth documenting for any future engine swap (we'd lose
  the free tumble).
- **pxMode=True sprites** are inherently 2D (camera-facing stickers).
  Anything that needs depth must be real geometry.
- **Sway amplitude as parallax cue** worked better than expected. Static
  visual depth perception was weak even with size+opacity taper; motion
  parallax fixed it cleanly without changing the camera.

### Sprint 1 -- Project init + hello world + backlog (~4 SP)

First sprint of the 3Dcockpit project. Goal was to prove the basic stack
works and capture the design before building. No real visual progress
beyond a single labeled bubble; that's deliberate.

| Item | SP |
|------|----|
| `3Dcockpit_poc.py` step 1: PyQtGraph + PyQt5 + PyOpenGL installed on Python 3.14, GLViewWidget + GLGridItem + single GLScatterPlotItem + GLTextItem rendering. Verified hardware-accelerated 3D works on the dev machine, GLTextItem available (pyqtgraph 0.14.0 OK), camera controls feel right under mouse. PyOpenGL_accelerate not required for this scale. | 2 |
| Architectural decisions captured before any visual build-out: (a) subprocess integration path when graduating to cockpit (tkinter + PyQt won't coexist cleanly in one process), (b) reuse `theme.VERDICT_BG` palette not `scoring.VERDICT_COLORS` (the dark-tuned palette is the right one), (c) fake-blur via per-tier opacity + desaturation before reaching for real shaders, (d) cursor-as-focal-point not hover-on-specific-bubble (cursor is a focus *zone* in screen space; distance falloff drives sharpness, multiple bubbles can be in focus at once), (e) screen-space 2D projection for picking over 3D raycasting at this scale. | 1 |
| Read of main cockpit source (scoring.py, app.py CockpitTab, theme.py, fetch.py, portfolio_io.py, signal_log_core.py, BACKLOG.md, indicators.py) to ground the visual mapping in real `analyze_stock` dict shape and to mirror existing sprint conventions. Identified all visual ammunition per bubble: verdict, direction, catalyst (bool), t_bull/t_bear, f_green/f_red, fund_grade, sector, last_bar_date, reason. Sprint 2+ will choose what to actually use; not everything earns a visual channel. | -- |
| GitHub repo set up at Per1980/3Dcockpit (separate from per1980/cockpit). `.gitignore` and README.md added. Initial commit. | 1 |

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

- **Sprints completed:** 2
- **Story points shipped:** 20
