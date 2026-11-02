"""Reddit collage (2400 x 3200): Ptolemy's coordinates on his own grid, his coasts shrunk onto the real map, Britain and
India against reality, and the headline numbers. Light background; labels sit on plain paper or sea; numbers from
data/results.json."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MP
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json"); FIT = jload(f"{DATA}/fit.json")
P = pd.read_csv(f"{DATA}/places.csv", dtype={"id": str, "map": str}); P["ec"] = P.f1_km.map(errc)
A, B, Cc = FIT["F1"]["a"], FIT["F1"]["b"], FIT["F1"]["c"]
PAPER = "#EEE6D4"
fig = plt.figure(figsize=(8, 32 / 3), dpi=300, facecolor=BG)
fig.text(.04, .962, "Ptolemy's world, about AD 150,", fontproperties=DISPB, fontsize=21, color=FG)
fig.text(.04, .93, "set against the real one", fontproperties=DISP, fontsize=27, color=RED)
fig.text(.04, .91, f"His Geography lists the known world as {R['source']['with_coords']:,} longitudes and latitudes. I matched {R['match']['places']:,} of", fontsize=7.6, color=MUT)
fig.text(.04, .898, "his places to where they really are, and measured the error.", fontsize=7.6, color=MUT)

# 1. his coordinates on his own grid
a1 = fig.add_axes([.04, .5, .92, .365]); ptol_ax(a1, ext=(-2, 182, -22, 68), lw=.7)
a1.scatter(P.lon_o, P.lat_o, s=2.2, c=P.ec, linewidths=0, zorder=5)
H = [pe.withStroke(linewidth=2.6, foreground=PAPER)]
for t, x, y, ha in (("Britain turns east", 3, 65.6, "left"), ("Thule, 63°", 179, 64.4, "right"), ("parallel of Rhodes, 36°", 179, 37.4, "right"),
                    ("India, flattened", 100, 3, "center"), ("Taprobane, swollen", 126, -7, "center"), ("Kattigara", 166, -12, "center"), ("Cape Prason", 80, -18, "center"),
                    ("Alexandria", 60.5, 25.5, "center")):
    a1.text(x, y, t, fontsize=6.4, color=FG if t not in ("Thule, 63°", "parallel of Rhodes, 36°") else PTOL, ha=ha, va="center", path_effects=H, zorder=9)
a1.scatter([60.5], [31], s=16, facecolors="none", edgecolors=FG, linewidths=.8, zorder=7)
fig.text(.04, .872, "1. Ptolemy's coordinates, drawn on a plain grid of his degrees", fontproperties=DISPB, fontsize=10.5, color=FG)
fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=c, mec="none", ms=4.5, label=l) for c, l in zip(ERRC, ERRL)] + [Line2D([], [], color=PTOL, lw=1.2, label="his coasts, in the order he lists them")],
           loc="upper left", bbox_to_anchor=(.04, .5), ncol=3, frameon=False, fontsize=6.4, title=f"Error, once his longitudes are shrunk by {B:.2f}:", title_fontsize=6.6, alignment="left", columnspacing=1.2, handletextpad=.4)

# 2. his coasts shrunk onto the real map
a2 = fig.add_axes([.04, .195, .55, .21]); world(a2, (-16, 122, -20, 62), aspect_lat=30, land="#E4DCC8", lw=.25)
for c in COASTS:
    p = np.array(c["pts"]); a2.plot(A + B * p[:, 0], p[:, 1] + Cc, color=PTOL, lw=.6, alpha=.95)
T = np.array(SITE["taprobane"]); a2.add_patch(MP(np.c_[A + B * T[:, 0], T[:, 1] + Cc], closed=True, fc=PTOL, alpha=.18, ec="none"))
fig.text(.04, .43, f"2. His coasts on the real map, longitudes x{B:.2f}", fontproperties=DISPB, fontsize=10.5, color=FG)
fig.text(.04, .418, "brown: Ptolemy, after one stretch and shift; beige: the real coasts", fontsize=6.6, color=MUT)

# stats
st = [(f"x{B:.2f}", RED, f"the one correction that fits best:\nhis degrees are too wide. 500/700 = {R['fit']['stadia_ratio']:.3f},\nthe ratio his small Earth implies"),
      (f"{R['fit']['f0']['median_km']} to {R['fit']['f1']['median_km']} km", BLUE, "median error, as written and\nafter shrinking his longitudes"),
      (f"{R['scotland']['turn']:.0f}°", "#2E8A6E", "Scotland turned clockwise,\nrelative to England"),
      (f"{R['taprobane']['area_ratio']:.0f}x", GOLD, "the area of his Sri Lanka,\nagainst the real island")]
for i, (big, col, small) in enumerate(st):
    y = .435 - i * .066
    fig.text(.63, y, big, fontproperties=DISP, fontsize=17, color=col, va="top")
    fig.text(.63, y - .025, small, fontsize=6.2, color=FG, va="top", linespacing=1.3)


# 3 and 4. Britain and India against reality, same scale within each pair
def mini(box_p, box_r, rows, poly=None, coasts=None, title="", rl=(0, 0, 0, 0)):
    kp = lambda lo, la: (lo * B * np.cos(np.radians(la)) * 111.2, la * 111.2)
    kr = lambda lo, la: (lo * np.cos(np.radians(la)) * 111.2, la * 111.2)
    ap = fig.add_axes(box_p); ar = fig.add_axes(box_r)
    ap.set_facecolor(PAPER); ar.set_facecolor(SEA)
    px, py = kp(rows.lon_o.values, rows.lat_o.values); rx, ry = kr(rows.lon.values, rows.lat.values)
    for f in W["features"]:
        for ring in rings(f["geometry"]):
            if ((ring[:, 0] > rl[0]) & (ring[:, 0] < rl[2]) & (ring[:, 1] > rl[1]) & (ring[:, 1] < rl[3])).any():
                X, Y = kr(ring[:, 0], ring[:, 1]); ar.add_patch(MP(np.c_[X, Y], closed=True, fc=LAND, ec="white", lw=.2))
    for c in coasts or []:
        p = np.array(c); X, Y = kp(p[:, 0], p[:, 1]); ap.plot(X, Y, color=PTOL, lw=.6)
    ext = [(px, py), (rx, ry)]
    if poly is not None:
        X, Y = kp(poly[:, 0], poly[:, 1]); ap.add_patch(MP(np.c_[X, Y], closed=True, fc=LAND, ec=PTOL, lw=.7)); ext[0] = (np.r_[px, X], np.r_[py, Y])
    t = (rows.lat - rows.lat.min()) / (rows.lat.max() - rows.lat.min())
    cols = [plt.cm.viridis_r(.1 + .8 * v) for v in t]
    ap.scatter(px, py, s=3.5, c=cols, linewidths=0, zorder=5); ar.scatter(rx, ry, s=3.5, c=cols, linewidths=0, zorder=5)
    w_in, h_in = box_p[2] * 8, box_p[3] * 32 / 3
    span = max(max(e[0].max() - e[0].min() for e in ext) / w_in, max(e[1].max() - e[1].min() for e in ext) / h_in) * 1.12
    for ax, (X, Y) in zip((ap, ar), ext):
        cx, cy = (X.max() + X.min()) / 2, (Y.max() + Y.min()) / 2
        ax.set_xlim(cx - span * w_in / 2, cx + span * w_in / 2); ax.set_ylim(cy - span * h_in / 2, cy + span * h_in / 2); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([]); [s_.set_color(RULE) for s_ in ax.spines.values()]
    return ap, ar


BR = P[P.id.str.startswith("2.03.")]
mini([.04, .045, .105, .115], [.155, .045, .105, .115], BR, coasts=[c["pts"] for c in COASTS if c["sec"].startswith("2.03.")], rl=(-9, 49.5, 3, 59.5))
fig.text(.04, .175, "3. Britain", fontproperties=DISPB, fontsize=10, color=FG)
fig.text(.04, .163, "Ptolemy left, reality right, same scale", fontsize=6.2, color=MUT)
IN = P[P["map"].isin(["AS10", "AS12"])]
mini([.3, .045, .105, .115], [.415, .045, .105, .115], IN, poly=np.array(SITE["taprobane"]), rl=(66, 5, 90, 36))
fig.text(.3, .175, "4. India and Sri Lanka", fontproperties=DISPB, fontsize=10, color=FG)
fig.text(.3, .163, "Ptolemy left, reality right, same scale", fontsize=6.2, color=MUT)
fig.text(.555, .155, "Dots coloured by real latitude,\nlight in the south, dark in the north.\nHis Scotland points east; his India\nis flat and his Taprobane crosses\nthe equator.", fontsize=6.2, color=FG, va="top", linespacing=1.35)
fig.text(.04, .022, "Sources: Grasshoff and Defaux (2019) Catalog of Ptolemy's Geography, CC BY 4.0; Pleiades (CC BY 3.0); Digital Atlas of the Roman Empire (CC BY-SA);", fontsize=5.5, color=MUT)
fig.text(.04, .012, "Natural Earth. Identifications by the catalogue's editors. Dr Tristan Hotham · maps.tristanhotham.com/ptolemy", fontsize=5.5, color=MUT)
out = os.path.join(ROOT, "reddit", "ptolemy_world.png")
fig.savefig(out, dpi=300, facecolor=BG); plt.close(fig)
from PIL import Image
assert Image.open(out).size == (2400, 3200), Image.open(out).size
print("collage", out)
