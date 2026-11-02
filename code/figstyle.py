"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the palette, Natural Earth outlines and Ptolemy's coasts."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERI = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-It.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#68625A", "axes.labelcolor": "#22201C",
                     "xtick.color": "#68625A", "ytick.color": "#68625A"})
BG, FG, MUT, LAND, RULE, SEA = "#F7F2E7", "#22201C", "#68625A", "#E7DFCB", "#E0D6C1", "#E9EEEC"
RED, BLUE, GOLD, PTOL = "#B23A2A", "#2F5FA7", "#B07A12", "#9C4A1A"
ERRC = ["#2E8A6E", "#8DB255", "#E0A11B", "#D2622A", "#8E2A2A"]; ERRB = [100, 250, 500, 1000]
ERRL = ["under 100 km", "100 to 250 km", "250 to 500 km", "500 to 1,000 km", "over 1,000 km"]
CONTC = {"Europe": BLUE, "Africa": GOLD, "Asia": RED}
errc = lambda km: ERRC[sum(km >= b for b in ERRB)]
RCOL = ["#2E8A6E", "#5D8F9E", "#2F5FA7", "#6E4C9A", "#B07A12", "#9C6B3A", "#C2412D", "#8E3B2E", "#D46A8C", "#3B7DD8", "#7A9A3A", "#E0A11B", "#3B3B3B"]
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


def world(ax, ext, land=LAND, ec="#FFFFFF", lw=.4, sea=SEA, aspect_lat=None):
    """Plate carree map with the cosine of the mid latitude as aspect, so shapes are not squashed."""
    ax.set_facecolor(sea)
    for f in W["features"]:
        for r in rings(f["geometry"]):
            ax.add_patch(MPoly(r, closed=True, fc=land, ec=ec, lw=lw, zorder=1))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_aspect(1 / np.cos(np.radians(aspect_lat if aspect_lat is not None else (ext[2] + ext[3]) / 2)))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

COASTS = jload(f"{DATA}/coasts.json")


def ptol_ax(ax, ext=(-2, 182, -22, 66), grid=True, lw=1.1):
    """Ptolemy's degrees on a plain grid, longitude drawn at its width on the parallel of Rhodes (36 degrees)."""
    ax.set_facecolor("#EEE6D4")
    if grid:
        for lo in range(0, 181, 10):
            ax.plot([lo, lo], [-20, 64], color=RULE, lw=.6, zorder=0)
        for la in range(-20, 61, 10):
            ax.plot([0, 180], [la, la], color=RULE, lw=.6, zorder=0)
        for la in (36, 63):
            ax.plot([0, 180], [la, la], color=PTOL, lw=.6, ls=(0, (3, 3)), alpha=.6, zorder=0)
    for c in COASTS:
        p = np.array(c["pts"]); ax.plot(p[:, 0], p[:, 1], color=PTOL, lw=lw, alpha=.85, zorder=2, solid_joinstyle="round")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1 / np.cos(np.radians(36)))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
