"""
3Dcockpit_poc.py -- Sprint 2 v3: real spheres + free orbit + NOW BUY sprinkle

Changes from v2:
  - Bubbles are now actual 3D sphere meshes (GLMeshItem), not 2D point
    sprites. They have real geometry, shaded by the 'balloon' shader so
    they read as volume.
  - GLViewWidget subclassed to remove the elevation clamp. You can now
    tumble the camera fully around any axis.
  - Each bubble has a main sphere + a larger soft-glow shell (additive-
    ish translucent). NOW BUY tier glow is much wider and brighter; back
    tiers have minimal halo.
  - NOW BUY / GET READY / WARMING get a per-bubble size pulse layered
    on top of the sway. NOW BUY pulses hardest. Sell side stays static.

Run: python 3Dcockpit_poc.py
"""
import sys
import hashlib
import json
import random
from pathlib import Path

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl

sys.path.insert(0, str(Path(__file__).parent.parent))
from theme import VERDICT_BG, BG


# =============================================================================
#  CONFIGURATION
# =============================================================================

VERDICT_ORDER = ["NOW BUY", "GET READY", "WARMING",
                 "CAUTION", "WATCH OUT", "NOW SELL"]

TIER_Y = {
    "NOW BUY":   +10.0, "GET READY":  +6.0, "WARMING":    +2.0,
    "CAUTION":    -2.0, "WATCH OUT":  -6.0, "NOW SELL":  -10.0,
}

# Per-tier visual: (radius, opacity, desat, glow_radius_mult, glow_alpha)
# Front tier has biggest core AND biggest/brightest glow.
TIER_TAPER = {
    "NOW BUY":   (1.50, 1.00, 0.00, 3.0, 0.45),
    "GET READY": (1.20, 0.92, 0.18, 2.0, 0.30),
    "WARMING":   (0.95, 0.78, 0.34, 1.7, 0.22),
    "CAUTION":   (0.72, 0.55, 0.55, 1.5, 0.16),
    "WATCH OUT": (0.55, 0.38, 0.70, 1.4, 0.12),
    "NOW SELL":  (0.42, 0.22, 0.85, 1.3, 0.08),
}

TIER_SWAY_AMP = {
    "NOW BUY":   0.55, "GET READY": 0.42, "WARMING":   0.32,
    "CAUTION":   0.22, "WATCH OUT": 0.14, "NOW SELL":  0.06,
}

TIER_BASE_FREQ = {
    "NOW BUY":   0.40, "GET READY": 0.32, "WARMING":   0.26,
    "CAUTION":   0.20, "WATCH OUT": 0.14, "NOW SELL":  0.08,
}

# Size pulse: (amplitude, freq Hz). Buy side breathes. Sell side static.
TIER_PULSE = {
    "NOW BUY":   (0.10, 0.55),
    "GET READY": (0.05, 0.40),
    "WARMING":   (0.025, 0.30),
    "CAUTION":   (0.0, 0.0),
    "WATCH OUT": (0.0, 0.0),
    "NOW SELL":  (0.0, 0.0),
}

SWAY_AXIS = np.array([0.75, 0.20, 0.75], dtype=np.float32)

VERDICT_WEIGHTS = {
    "NOW BUY":   0.10, "GET READY": 0.13, "WARMING":   0.15,
    "CAUTION":   0.39, "WATCH OUT": 0.15, "NOW SELL":  0.08,
}

GREY = (0.24, 0.24, 0.27)


# =============================================================================
#  HELPERS
# =============================================================================

def hash_seed(ticker, salt=0):
    h = hashlib.md5(f"{ticker}{salt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

def blend_toward_grey(rgb, amount):
    return tuple(c * (1 - amount) + g * amount for c, g in zip(rgb, GREY))

def assign_verdict(ticker):
    rnd = random.Random(hash_seed(ticker))
    r = rnd.random()
    cumulative = 0.0
    for verdict, weight in VERDICT_WEIGHTS.items():
        cumulative += weight
        if r < cumulative:
            return verdict
    return "CAUTION"

def position_in_tier(ticker, tier):
    rnd = random.Random(hash_seed(ticker, salt=1))
    x = (rnd.random() - 0.5) * 18.0
    z = (rnd.random() - 0.5) * 6.0
    y_jitter = (rnd.random() - 0.5) * 0.8
    return x, TIER_Y[tier] + y_jitter, z

def bubble_phase(ticker):
    rnd = random.Random(hash_seed(ticker, salt=2))
    return rnd.random() * 2 * np.pi

def bubble_freq_mult(ticker):
    rnd = random.Random(hash_seed(ticker, salt=3))
    return 0.8 + rnd.random() * 0.4


# =============================================================================
#  DATA
# =============================================================================

def load_portfolio():
    path = Path(__file__).parent.parent / "portfolio.json"
    if not path.exists():
        return [("GOMX.ST", "GomSpace"), ("NKT.CO", "NKT")]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [(ticker, meta.get("name", ticker)) for ticker, meta in data.items()]


# =============================================================================
#  FREE-ORBIT CAMERA
# =============================================================================

class FreeOrbitView(gl.GLViewWidget):
    """GLViewWidget with the elevation clamp removed. Full tumble."""

    def orbit(self, azim, elev):
        self.opts['azimuth'] += azim
        # No clamp; just wrap into [-180, 180] so the number stays finite.
        e = self.opts['elevation'] + elev
        self.opts['elevation'] = ((e + 180.0) % 360.0) - 180.0
        self.update()


# =============================================================================
#  SCENE
# =============================================================================

def build_starfield(view, n_stars=1500):
    rng = np.random.default_rng(42)
    pos = rng.normal(size=(n_stars, 3))
    pos = pos / np.linalg.norm(pos, axis=1, keepdims=True)
    pos = pos * rng.uniform(25, 80, size=(n_stars, 1))

    brightness = rng.uniform(0.15, 0.55, size=n_stars)
    tint = rng.choice([0, 1, 2], size=n_stars)
    colors = np.zeros((n_stars, 4), dtype=np.float32)
    for i, (b, t) in enumerate(zip(brightness, tint)):
        if t == 0:    colors[i] = [b, b, b, b * 0.8]
        elif t == 1:  colors[i] = [b, b * 0.9, b * 0.7, b * 0.7]
        else:         colors[i] = [b * 0.7, b * 0.85, b, b * 0.7]
    sizes = rng.uniform(0.8, 2.4, size=n_stars).astype(np.float32)
    view.addItem(gl.GLScatterPlotItem(pos=pos.astype(np.float32),
                                      color=colors, size=sizes, pxMode=True))


def make_sphere_mesh(radius):
    """One MeshData per tier-radius, shared across all bubbles in that tier."""
    return gl.MeshData.sphere(rows=10, cols=18, radius=radius)


def build_bubbles(view, portfolio):
    """
    Returns state dict {verdict: tier_state}. Tier state holds positions,
    phases/freqs, and lists of GLMeshItems the animator mutates per frame.
    """
    by_verdict = {v: [] for v in VERDICT_ORDER}
    for ticker, name in portfolio:
        by_verdict[assign_verdict(ticker)].append((ticker, name))

    state = {}

    # Back-to-front so blending order is sane on opaque sections.
    for verdict in reversed(VERDICT_ORDER):
        tickers = by_verdict[verdict]
        if not tickers:
            continue

        radius, opacity, desat, glow_mult, glow_alpha = TIER_TAPER[verdict]
        rgb = blend_toward_grey(hex_to_rgb(VERDICT_BG[verdict]), desat)
        core_color = (*rgb, opacity)
        glow_color = (*rgb, opacity * glow_alpha)

        # Shared geometry within the tier.
        main_md = make_sphere_mesh(radius)
        glow_md = make_sphere_mesh(radius * glow_mult)

        positions = np.array([position_in_tier(t, verdict)
                              for t, _ in tickers], dtype=np.float32)
        phases = np.array([bubble_phase(t) for t, _ in tickers],
                          dtype=np.float32)
        freqs = np.array([TIER_BASE_FREQ[verdict] * bubble_freq_mult(t)
                          for t, _ in tickers], dtype=np.float32)

        bubbles = []
        for (ticker, _), pos in zip(tickers, positions):
            glow = gl.GLMeshItem(meshdata=glow_md, smooth=True,
                                 shader='balloon', color=glow_color,
                                 glOptions='translucent')
            view.addItem(glow)

            main = gl.GLMeshItem(meshdata=main_md, smooth=True,
                                 shader='balloon', color=core_color,
                                 glOptions='translucent')
            view.addItem(main)

            label_alpha = int(opacity * 220)
            label = gl.GLTextItem(pos=pos.tolist(), text=ticker,
                                  color=(210, 215, 230, label_alpha))
            view.addItem(label)

            bubbles.append({"main": main, "glow": glow, "label": label})

        state[verdict] = {
            "positions": positions,
            "phases":    phases,
            "freqs":     freqs,
            "bubbles":   bubbles,
        }
    return state


# =============================================================================
#  ANIMATION
# =============================================================================

class SwayAnimator:
    """Per-frame: sway translation + (front-tier) size pulse."""
    FPS = 30
    DT = 1.0 / FPS

    def __init__(self, state):
        self.state = state
        self.t = 0.0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(int(1000 / self.FPS))

    def step(self):
        self.t += self.DT
        for verdict, tier in self.state.items():
            amp = TIER_SWAY_AMP[verdict]
            pulse_amp, pulse_freq = TIER_PULSE[verdict]
            phases = tier["phases"]

            # Sway: Lissajous offset per bubble.
            arg = 2 * np.pi * tier["freqs"] * self.t + phases
            offsets = (np.column_stack([
                np.sin(arg),
                np.sin(arg + np.pi / 3),
                np.cos(arg + np.pi / 4),
            ]).astype(np.float32) * amp * SWAY_AXIS)

            # Size pulse (front tiers only).
            if pulse_amp > 0:
                pulses = 1.0 + pulse_amp * np.sin(
                    2 * np.pi * pulse_freq * self.t + phases)
            else:
                pulses = np.ones(len(phases), dtype=np.float32)

            new_pos = tier["positions"] + offsets

            for i, bubble in enumerate(tier["bubbles"]):
                m = QtGui.QMatrix4x4()
                m.translate(float(new_pos[i, 0]),
                            float(new_pos[i, 1]),
                            float(new_pos[i, 2]))
                if pulse_amp > 0:
                    s = float(pulses[i])
                    m.scale(s, s, s)
                bubble["main"].setTransform(m)
                bubble["glow"].setTransform(m)
                bubble["label"].setData(pos=new_pos[i].tolist())


# =============================================================================
#  MAIN
# =============================================================================

def build_view():
    view = FreeOrbitView()
    view.setWindowTitle("3Dcockpit - Sprint 2 v3")
    view.resize(1400, 900)
    view.setBackgroundColor(BG)
    view.setCameraPosition(distance=44, elevation=10, azimuth=90)

    build_starfield(view)
    state = build_bubbles(view, load_portfolio())
    return view, state


def main():
    app = QtWidgets.QApplication(sys.argv)
    view, state = build_view()
    animator = SwayAnimator(state)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
