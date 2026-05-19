# 3Dcockpit

3D depth-tiered verdict visualization. Companion project to the main
cockpit trading-analysis tool. Lives as a subfolder of the cockpit
working tree (`CockpitV1_1/3Dcockpit/`) but is its own separate git
repository.

Renders portfolio tickers as bubbles in a 3D scene. Z-depth is driven
by verdict severity:

- NOW BUY     -> closest to camera, sharp, full color
- GET READY   -> behind
- WARMING     -> further back
- CAUTION     -> further, desaturated
- WATCH OUT   -> deep, dim
- NOW SELL    -> deepest, most washed-out

Plus a cursor-as-focal-point overlay: bubbles near the mouse sharpen
up; distant ones blur/dim. Tier baseline plus cursor-proximity overlay
run together.

Discipline angle: green sits where attention naturally lands. Sell
signals stay visible but recessed until deliberately pointed at.

## Stack

- Python 3.14
- PyQtGraph 0.14 (OpenGL 3D)
- PyQt5
- PyOpenGL
- NumPy

## Quick start

From the cockpit folder:

```
cd 3Dcockpit
python 3Dcockpit_poc.py
```

Install deps if not already present:

```
pip install pyqtgraph PyQt5 PyOpenGL numpy
```

## Relationship to the main cockpit

Main cockpit codebase is **read-only** from this project. When the
visualization needs real data (Tier 2 #9 in the backlog), it imports
from the parent folder using `..\\` relative paths -- never mutates
anything over there. Any required upstream change is filed as a
request in the main `BACKLOG.md`, not edited from here.

## File naming

All Python files in this project use the `3D` prefix
(`3Dcockpit_poc.py`, `3Dbacklog.md`, etc.) so they're instantly
distinguishable from cockpit files when both projects' files are
visible at once in the editor. `README.md` and `.gitignore` are
exempt because GitHub and git respectively require those exact
filenames.

## Status

Sprint 1 complete: hello-world bubble rendering, backlog drafted,
repo set up. See `3Dbacklog.md` for what's next.
