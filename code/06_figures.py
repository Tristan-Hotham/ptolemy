"""Header card, blog figures (release/blog/b_*.png, 1800 px wide) and paper figures (release/paper/f_*.png).
Numbers from data/results.json; places from data/places.csv; coasts from data/coasts.json."""
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon as MP
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json"); FIT = jload(f"{DATA}/fit.json")
P = pd.read_csv(f"{DATA}/places.csv", dtype={"id": str, "map": str})
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
os.makedirs(BL, exist_ok=True); os.makedirs(PA, exist_ok=True)
A, B, Cc = FIT["F1"]["a"], FIT["F1"]["b"], FIT["F1"]["c"]
HALO = [pe.withStroke(linewidth=3.2, foreground="#FFFCF4")]
P["ec"] = P.f1_km.map(errc)
byid = P.set_index("id")


def both(fig, name, blog=True):
    fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    if blog:
        fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def label(ax, x, y, t, dx=0, dy=0, ha="left", fs=9, col=FG, weight=None):
    ax.annotate(t, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=fs, color=col, path_effects=HALO, zorder=8, fontweight=weight)


def err_legend(fig, x, y, ncol=5, fs=9.5):
    fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=c, mec="white", ms=7, label=l) for c, l in zip(ERRC, ERRL)] +
               [Line2D([], [], color=PTOL, lw=1.6, label="Ptolemy's coasts")], loc="lower left", bbox_to_anchor=(x, y), ncol=ncol, frameon=False, fontsize=fs,
               title="Error after shrinking his longitudes by %.2f" % B, title_fontsize=fs, alignment="left")


LAB = [("2.03.27.02", "London"), ("3.01.61.02", "Rome"), ("4.05.09.03", "Alexandria"), ("2.04.16.03", "Cadiz"), ("6.11.09.03", "Samarkand"), ("7.01.73.03", "Patna"),
       ("7.04.04.08", "Dondra Head"), ("6.16.08.07", "Sera (Xi'an)"), ("7.03.03.07", "Kattigara"), ("4.08.02.01", "Cape Prason"), ("2.03.05.03", "Duncansby Head")]
OFF_P = {"London": (-7, 0, "right"), "Rome": (0, 9, "center"), "Alexandria": (0, -9, "center"), "Cadiz": (0, -9, "center"), "Samarkand": (0, 9, "center"), "Patna": (0, 9, "center"),
         "Dondra Head": (7, -4, "left"), "Sera (Xi'an)": (-7, 0, "right"), "Kattigara": (-7, 0, "right"), "Cape Prason": (7, -4, "left"), "Duncansby Head": (6, 7, "left")}
OFF_W = {"London": (-7, 0, "right"), "Rome": (0, 9, "center"), "Alexandria": (0, -9, "center"), "Cadiz": (-7, -3, "right"), "Samarkand": (0, 9, "center"), "Patna": (0, 9, "center"),
         "Dondra Head": (7, -4, "left"), "Sera (Xi'an)": (0, 9, "center"), "Kattigara": (7, -4, "left"), "Cape Prason": (7, -4, "left"), "Duncansby Head": (6, 6, "left")}

# ---------- 1. the two maps ----------
fig = plt.figure(figsize=(12, 6.0), facecolor=BG)
a1 = fig.add_axes([.01, .17, .49, .68]); a2 = fig.add_axes([.51, .17, .48, .68])
ptol_ax(a1, ext=(-2, 182, -22, 66))
a1.scatter(P.lon_o, P.lat_o, s=7, c=P.ec, edgecolors="white", linewidths=.2, zorder=5)
world(a2, (-20, 125, -22, 64), aspect_lat=30)
a2.scatter(P.lon, P.lat, s=7, c=P.ec, edgecolors="white", linewidths=.2, zorder=5)
for i, t in LAB:
    r = byid.loc[i]; dx, dy, ha = OFF_P[t]; label(a1, r.lon_o, r.lat_o, t, dx, dy, ha, fs=8)
    dx, dy, ha = OFF_W[t]; label(a2, r.lon, r.lat, t, dx, dy, ha, fs=8)
fig.text(.01, .94, "Ptolemy's coordinates, about AD 150", fontproperties=DISPB, fontsize=15, color=FG)
fig.text(.01, .895, "his degrees on a plain grid; brown: his coasts, joined in the order he lists them", fontsize=8.6, color=MUT)
fig.text(.51, .94, "The same places today", fontproperties=DISPB, fontsize=15, color=FG)
fig.text(.51, .895, f"{R['match']['places']:,} places matched to their real positions", fontsize=8.6, color=MUT)
err_legend(fig, .01, .02, ncol=6, fs=8.6)
both(fig, "maps")

# ---------- 2. his coasts shrunk onto the real map ----------
fig = plt.figure(figsize=(12, 8.9), facecolor=BG); ax = fig.add_axes([.01, .03, .98, .84])
world(ax, (-16, 122, -20, 62), aspect_lat=30, land="#E4DCC8")
for c in COASTS:
    p = np.array(c["pts"]); ax.plot(A + B * p[:, 0], p[:, 1] + Cc, color=PTOL, lw=1.2, alpha=.9, zorder=3, solid_joinstyle="round")
T = np.array(SITE["taprobane"]); ax.add_patch(MP(np.c_[A + B * T[:, 0], T[:, 1] + Cc], closed=True, fc=PTOL, alpha=.15, ec="none", zorder=2))
for i in ("7.03.03.07", "4.08.02.01"):
    r = byid.loc[i]; ax.scatter([A + B * r.lon_o], [r.lat_o + Cc], s=30, c=PTOL, zorder=6, edgecolors="white", linewidths=.6)
for t, lo, la, ha in (("Scotland, turned east", 9, 60.6, "left"), ("India, flattened", 72, 17.5, "left"), ("Taprobane, swollen", 79, -3.5, "left"),
                      ("Kattigara", 113, -8.4, "right"), ("Cape Prason", 46.5, -15, "left"), ("the Caspian, as wide as it is long", 66, 46, "left")):
    ax.text(lo, la, t, fontsize=9.5, color=PTOL, ha=ha, va="center", path_effects=HALO, zorder=9)
fig.text(.01, .955, f"Ptolemy's coasts laid on the real map, his longitudes shrunk by {B:.2f}", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.01, .925, "Brown: his coastal points joined in the order he lists them, moved by the single best stretch and shift. Grey: Natural Earth.", fontsize=9.5, color=MUT)
both(fig, "overlay")

# ---------- 3. the stretch ----------
fig, ax = plt.subplots(figsize=(12, 7), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.08, right=.97, top=.86, bottom=.1)
for k, col in CONTC.items():
    d = P[P.continent == k]; ax.scatter(d.dlon_true, d.dlon_ptol, s=14, c=col, alpha=.75, edgecolors="white", linewidths=.3, label=k, zorder=3)
xs = np.array([-50, 85]); s = R["stretch"]["slope_alex"]
ax.plot(xs, xs, ls="--", color=MUT, lw=1.2, zorder=2); ax.plot(xs, xs * s, color=FG, lw=1.6, zorder=2)
ax.text(68, 64, "a true map", fontsize=10, color=MUT, ha="left"); ax.text(52, 52 * s + 6, f"Ptolemy: x{s:.2f}", fontsize=11, color=FG, ha="right")
ax.set_xlim(-50, 85); ax.set_ylim(-70, 125); ax.grid(color=RULE); ax.set_axisbelow(True); spines(ax)
ax.set_xlabel("real longitude east of Alexandria (degrees)"); ax.set_ylabel("Ptolemy's longitude east of Alexandria")
ax.legend(loc="upper left", frameon=False, fontsize=10.5)
fig.text(.02, .93, f"Every 10 degrees of real longitude become {R['stretch']['per10']:.1f} of Ptolemy's", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.02, .895, f"{R['match']['places']:,} matched places, measured from Alexandria, where he worked", fontsize=9.5, color=MUT)
both(fig, "stretch")

# ---------- 4. error and distance from Alexandria ----------
D = R["alex_bins"]
fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.08, right=.97, top=.84, bottom=.16)
x = np.arange(len(D)); w = .36
ax.bar(x - w / 2, [d["f0_km"] for d in D], w, color=RED, alpha=.88, label="as written, aligned on Alexandria")
ax.bar(x + w / 2, [d["f1_km"] for d in D], w, color=BLUE, alpha=.88, label=f"longitudes shrunk by {B:.2f}")
for i, d in enumerate(D):
    ax.text(i - w / 2, d["f0_km"] + 20, f"{d['f0_km']:,}", ha="center", fontsize=10); ax.text(i + w / 2, d["f1_km"] + 20, f"{d['f1_km']:,}", ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels([(f"{d['lo']:,} to {d['hi']:,} km" if d["hi"] < 9000 else f"over {d['lo']:,} km") + f"\n{d['n']} places" for d in D], fontsize=10)
ax.set_ylabel("median error (km)"); spines(ax); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.legend(frameon=False, loc="upper left", fontsize=10.5)
fig.text(.02, .93, "The farther from Alexandria, the worse the map, until the longitudes are shrunk", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.02, .89, "Median error for places in bands of distance from Alexandria", fontsize=9.5, color=MUT)
both(fig, "alex")


# ---------- twin shape figures ----------
def km_p(lo, la): return lo * B * np.cos(np.radians(la)) * 111.2, la * 111.2
def km_r(lo, la): return lo * np.cos(np.radians(la)) * 111.2, la * 111.2


def twin(rows, realbox, title, sub, name, labels, coasts=None, poly=None, realpoly=None, colours=None, blog=True):
    fig = plt.figure(figsize=(12, 7), facecolor=BG)
    a1 = fig.add_axes([.02, .05, .46, .78]); a2 = fig.add_axes([.52, .05, .46, .78])
    px, py = km_p(rows.lon_o.values, rows.lat_o.values); rx, ry = km_r(rows.lon.values, rows.lat.values)
    a1.set_facecolor("#EEE6D4"); a2.set_facecolor(SEA)
    for f in W["features"]:
        for ring in rings(f["geometry"]):
            if ((ring[:, 0] > realbox[0]) & (ring[:, 0] < realbox[2]) & (ring[:, 1] > realbox[1]) & (ring[:, 1] < realbox[3])).any():
                X, Y = km_r(ring[:, 0], ring[:, 1]); a2.add_patch(MP(np.c_[X, Y], closed=True, fc=LAND, ec="white", lw=.4, zorder=1))
    if realpoly is not None:
        X, Y = km_r(realpoly[:, 0], realpoly[:, 1]); a2.add_patch(MP(np.c_[X, Y], closed=True, fc=SEA, ec=MUT, lw=.8, zorder=1.5))
    for c in coasts or []:
        p = np.array(c); X, Y = km_p(p[:, 0], p[:, 1]); a1.plot(X, Y, color=PTOL, lw=1.2, zorder=2)
    if poly is not None:
        X, Y = km_p(poly[:, 0], poly[:, 1]); a1.add_patch(MP(np.c_[X, Y], closed=True, fc=LAND, ec=PTOL, lw=1.4, zorder=1.5))
    t = (rows.lat - rows.lat.min()) / max(1e-6, rows.lat.max() - rows.lat.min())
    cols = colours if colours is not None else [plt.cm.viridis_r(.1 + .8 * v) for v in t]
    a1.scatter(px, py, s=26, c=cols, edgecolors="white", linewidths=.5, zorder=5); a2.scatter(rx, ry, s=26, c=cols, edgecolors="white", linewidths=.5, zorder=5)
    sp = max(px.max() - px.min(), rx.max() - rx.min(), (realbox[2] - realbox[0]) * 111.2 * np.cos(np.radians(realbox[1])) * .2) * 1.12
    sq = max(py.max() - py.min(), ry.max() - ry.min()) * 1.12
    if poly is not None:
        X, Y = km_p(poly[:, 0], poly[:, 1]); sq = max(sq, (max(py.max(), Y.max()) - min(py.min(), Y.min())) * 1.12)
    for ax, X, Y in ((a1, px, py), (a2, rx, ry)):
        cx, cy = (X.max() + X.min()) / 2, (Y.max() + Y.min()) / 2
        if ax is a1 and poly is not None:
            PX, PY = km_p(poly[:, 0], poly[:, 1]); cy = (max(Y.max(), PY.max()) + min(Y.min(), PY.min())) / 2
        h = max(sq, sp * .78 / .46 * .46 / .78) / 2; wd = h * (.46 * 12) / (.78 * 7)
        ax.set_xlim(cx - wd, cx + wd); ax.set_ylim(cy - h, cy + h); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color(RULE)
    for i, tx, d1, d2 in labels:
        j = list(rows.id).index(i)
        label(a1, px[j], py[j], tx, d1[0], d1[1], "right" if d1[0] < 0 else "left", fs=9.5)
        label(a2, rx[j], ry[j], tx, d2[0], d2[1], "right" if d2[0] < 0 else "left", fs=9.5)
    x0, x1 = a1.get_xlim(); y0, _ = a1.get_ylim(); L = 200
    a1.plot([x1 - (x1 - x0) * .05 - L, x1 - (x1 - x0) * .05], [y0 + (x1 - x0) * .04] * 2, color=FG, lw=2); a1.text(x1 - (x1 - x0) * .05, y0 + (x1 - x0) * .06, "200 km", ha="right", fontsize=9)
    fig.text(.02, .935, title, fontproperties=DISPB, fontsize=17, color=FG); fig.text(.02, .895, sub, fontsize=9.5, color=MUT)
    fig.text(.02, .845, "Ptolemy's coordinates", fontsize=10.5, color=FG, fontweight="bold"); fig.text(.52, .845, "Reality", fontsize=10.5, color=FG, fontweight="bold")
    both(fig, name, blog)


BR = P[P.id.str.startswith("2.03.")]
sc = R["scotland"]
twin(BR, (-9, 49.5, 3, 59.5), f"Britain: Scotland turned {sc['turn']:.0f} degrees east",
     f"Solway to Duncansby Head: bearing {sc['brg_true']} degrees in reality, {sc['brg_ptol']} on Ptolemy's map. Dots coloured by real latitude, same scale on both sides.", "britain",
     [("2.03.27.02", "London", (7, 3), (7, 3)), ("2.03.17.01", "York", (7, -3), (7, -3)), ("2.03.05.03", "Duncansby Head", (-7, -8), (7, 0)), ("2.03.01.08", "Mull of Kintyre", (-7, 9), (-7, 0)),
      ("2.03.03.10", "Land's End", (7, -4), (-7, 0)), ("2.03.02.08", "Solway", (-7, 6), (-7, 6))], coasts=[c["pts"] for c in COASTS if c["sec"].startswith("2.03.")])
IN = P[P["map"].isin(["AS10", "AS12"])]
tp = R["taprobane"]
twin(IN, (66, 5, 90, 36), f"India flattened, Taprobane {tp['area_ratio']:.0f} times too big",
     f"Barygaza to Cape Komaria: {R['india']['lat_span_ptol']} degrees of latitude on Ptolemy's map, {R['india']['lat_span_true']} in reality. Brown: his Taprobane. Same scale.", "india",
     [("7.01.62.04", "Barygaza", (-7, 0), (-7, 0)), ("7.01.09.06", "Cape Komaria", (-7, -8), (-7, -6)), ("7.01.73.03", "Patna", (7, 3), (7, 3)), ("7.01.45.05", "Taxila", (7, -3), (7, -3)),
      ("7.04.04.08", "Dondra Head", (7, -4), (7, -4))], poly=np.array(SITE["taprobane"]))
CS = ["5.09.12.05", "5.09.12.03", "5.09.12.04", "5.12.02.03", "5.12.02.07", "5.12.01.07", "6.02.02.03", "6.14.02.04", "6.09.01.05", "6.14.02.05"]
CA = P.set_index("id").loc[CS].reset_index()
twin(CA, (44, 35, 64, 49), "The Caspian: an enclosed sea of the wrong shape",
     "Blue: river mouths on the Caspian shore; gold: the Oxus and Jaxartes, which Ptolemy brings to the Caspian and which really reach the Aral Sea. Same scale.", "caspian",
     [("5.09.12.05", "Volga", (7, 3), (7, -4)), ("6.14.02.04", "Ural", (7, 4), (7, 4)), ("5.12.01.07", "Kura", (-7, 0), (-7, 0)), ("6.02.02.03", "Sefid Rud", (-7, -6), (7, -4)),
      ("6.09.01.05", "Oxus", (7, 0), (7, 0)), ("6.14.02.05", "Jaxartes", (7, 4), (7, 4))],
     coasts=[c["pts"] for c in COASTS if c["sec"] in ("5.09.12", "5.12.02", "6.02.02", "6.09.02", "6.14.02")], realpoly=np.array(SITE["caspian"]),
     colours=[GOLD if i in ("6.09.01.05", "6.14.02.05") else BLUE for i in CA.id], blog=False)

# ---------- 7. regions ----------
RG = sorted([r for r in SITE["regions"] if r["ranked"]], key=lambda r: -r["shape_km"])
fig, ax = plt.subplots(figsize=(12, 7.4), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.24, right=.96, top=.86, bottom=.1)
for i, r in enumerate(RG):
    ax.barh(i, r["f1_km"], color=RULE, height=.72); ax.barh(i, r["shape_km"], color=CONTC[r["continent"]], height=.4)
    ax.text(max(r["f1_km"], r["shape_km"]) + 6, i, f"{r['shape_km']} / {r['f1_km']}", va="center", fontsize=9.5)
ax.set_yticks(range(len(RG))); ax.set_yticklabels([f"{r['name']} ({r['n']})" for r in RG], fontsize=10.5); ax.tick_params(axis="y", length=0)
spines(ax); ax.spines["left"].set_visible(False); ax.grid(axis="x", color=RULE); ax.set_axisbelow(True); ax.set_xlabel("median error (km)")
ax.legend(handles=[Patch(color=CONTC[k], label=f"shape, {k}") for k in CONTC] + [Patch(color=RULE, label="placement on the whole map")], loc="lower right", frameon=False, fontsize=10)
fig.text(.02, .93, "Best and worst: Ptolemy's regional maps", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.02, .89, f"Median error in each region's shape (its own best shift, turn and scale) and in its placement. Regional maps with at least {R['min_n']} places; number in brackets.", fontsize=9.3, color=MUT)
both(fig, "regions")

# ---------- 8. recensions ----------
H = SITE["rec_hist"]
fig, ax = plt.subplots(figsize=(12, 5.4), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.08, right=.97, top=.84, bottom=.14)
ax.bar(range(len(H)), [h["n"] for h in H], color=["#2E8A6E"] + [PTOL] * (len(H) - 1), alpha=.9)
for i, h in enumerate(H): ax.text(i, h["n"] + 40, f"{h['n']:,}", ha="center", fontsize=10.5)
ax.set_xticks(range(len(H))); ax.set_xticklabels([h["label"] for h in H], fontsize=10); spines(ax); ax.set_ylabel("entries"); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
fig.text(.02, .93, f"Omega and Xi agree exactly for {R['rec']['same_pct']:.0f}% of entries", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.02, .89, f"The {R['rec']['both']:,} entries with coordinates in both recensions, by the larger of the two differences in longitude and latitude", fontsize=9.5, color=MUT)
both(fig, "recensions", blog=False)

# ---------- header card 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
fig.text(.04, .8, "Ptolemy's", fontproperties=DISP, fontsize=58, color=FG)
fig.text(.04, .65, "World", fontproperties=DISP, fontsize=58, color=RED)
fig.text(.045, .55, "The Geography's coordinates, about AD 150,", fontproperties=SERP, fontsize=16, color=FG)
fig.text(.045, .505, "set against where the places really are", fontproperties=SERP, fontsize=16, color=FG)
fig.text(.045, .44, f"{R['match']['places']:,} places  ·  longitudes x{B:.2f}  ·  Sri Lanka {R['taprobane']['area_ratio']:.0f}x too big", fontsize=10.5, color=MUT)
a3 = fig.add_axes([.04, .04, .4, .36]); world(a3, (-16, 122, -20, 62), aspect_lat=30, land="#E4DCC8")
for c in COASTS:
    p = np.array(c["pts"]); a3.plot(A + B * p[:, 0], p[:, 1] + Cc, color=PTOL, lw=.6, alpha=.9)
a1 = fig.add_axes([.47, .06, .52, .88]); ptol_ax(a1, ext=(-2, 182, -22, 66), lw=.8)
a1.scatter(P.lon_o, P.lat_o, s=3, c=P.ec, linewidths=0, zorder=5)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
from PIL import Image as _I
assert _I.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
for f in os.listdir(BL):
    if f.startswith("b_"): assert _I.open(os.path.join(BL, f)).size[0] == 1800, f
print("figures", sorted(os.listdir(BL)), sorted(f for f in os.listdir(PA) if f.startswith("f_")))
