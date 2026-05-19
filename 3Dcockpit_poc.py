"""
3Dcockpit_poc.py - 3D verdict visualization PoC.
Step 1: scene + a single front-tier bubble with label.
Throwaway-friendly. Run: python 3Dcockpit_poc.py
"""
import sys
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph.opengl as gl


def build_view():
    view = gl.GLViewWidget()
    view.setWindowTitle("3Dcockpit - PoC step 1")
    view.resize(1200, 800)
    view.setBackgroundColor((10, 10, 14))

    # Camera convention picked here:
    #   +Y is the depth axis. Front tier (NOW BUY) sits at high Y, near camera.
    #   Back tier (NOW SELL) sits at low/negative Y, far from camera.
    #   Slight elevation so we get a perspective hint, not a flat head-on view.
    view.setCameraPosition(distance=22, elevation=12, azimuth=90)

    # Floor grid in XY plane. Pure depth cue for now. Retire it later
    # if it competes with the bubbles visually.
    grid = gl.GLGridItem()
    grid.setSize(x=24, y=24)
    grid.setSpacing(x=2, y=2)
    grid.setColor((80, 80, 100, 60))
    view.addItem(grid)

    # One test bubble at the "front" depth.
    pos = np.array([[0.0, 8.0, 0.0]])              # y=8 -> front tier
    color = np.array([[0.20, 1.00, 0.45, 1.0]])    # NOW BUY green, full opacity
    size = np.array([34.0])                        # pixel size (pxMode=True)

    bubble = gl.GLScatterPlotItem(pos=pos, color=color, size=size, pxMode=True)
    view.addItem(bubble)

    # Label. GLTextItem is camera-facing (billboarded).
    label = gl.GLTextItem(pos=(0.0, 8.0, 0.0), text="GOMX.ST")
    view.addItem(label)

    return view


def main():
    app = QtWidgets.QApplication(sys.argv)
    view = build_view()
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
