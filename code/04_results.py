"""Every number used anywhere (data/results.json), the regional table (data/regions.csv) and the page data
(data/site.json). Reads only data/.

Definitions
  * place: a catalogue entry with an Omega position whose editors' identification I matched to modern coordinates
    (02_geo.py), one per real place. Error: the great-circle distance between the real place and where a transform
    of Ptolemy's coordinates puts it (03_fit.py: F0 as written, aligned on Alexandria; F1 longitudes shrunk and
    shifted, latitudes shifted; F2 affine; F3 Helmert; F4 F1 by regional map; shape: Helmert by regional map).
  * Ptolemy's frame for directions and shapes: his degrees, with longitude differences multiplied by the cosine of
    the latitude (as on his own maps), so that a bearing on his map can be compared with a bearing on the globe.
  * Kilometres on Ptolemy's map: his degrees of latitude at 111.2 km and his degrees of longitude first shrunk by the
    fitted factor b (F1), so his map is compared with the world at the same overall scale.
  * Regions: Ptolemy's 26 regional maps; only those with at least MIN_N places are ranked."""
import numpy as np, pandas as pd
from shapely.geometry import shape, Polygon, Point
from pyproj import Transformer
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from shapely.ops import transform as stransform
from common import *

C = pd.read_csv(f"{DATA}/catalogue.csv", dtype={"id": str, "map": str})
C["ch"] = C.id.str[:4]
M = pd.read_csv(f"{DATA}/matches.csv", dtype={"id": str})
U = pd.read_csv(f"{DATA}/unmatched_points.csv", dtype={"id": str})
P = pd.read_csv(f"{DATA}/places.csv", dtype={"id": str, "map": str})
FIT = jload(f"{DATA}/fit.json")
W = jload(f"{DATA}/world.json"); CASP = shape(jload(f"{DATA}/caspian.json")["geometry"])
R = {}
pc = lambda a, b: round(100 * a / b, 1) if b else None
MIN_N = 15
D2R = np.pi / 180
B = FIT["F1"]["b"]
byid = P.set_index("id")
cat = C.set_index("id")

# ---------- source and matching ----------
X = C[C.has_o | C.has_x]
pts = X[X.ftype.isin(POINT_TYPES)]
R["source"] = {"rows": len(C), "with_coords": len(X), "omega": int(C.has_o.sum()), "xi": int(C.has_x.sum()), "both": int((C.has_o & C.has_x).sum()),
               "points": len(pts), "points_identified": int(pts.modern.notna().sum()), "identified_pct": pc(pts.modern.notna().sum(), len(pts)),
               "settlements": int((X.ftype == "settlement").sum()), "starred": int(X.starred.sum()), "chapters": int(C.ch.nunique()), "maps": int(C["map"].nunique()),
               "max_lon": float(X.lon_o.max()), "min_lon": float(X.lon_o.min()), "max_lat": round(float(X.lat_o.max()), 2), "min_lat": round(float(X.lat_o.min()), 2)}
R["match"] = {"matched": len(M), "omega": FIT["n_omega"], "places": len(P), "pct_of_identified": pc(len(M), R["source"]["points_identified"]),
              "high": int((P.confidence == "high").sum()), "medium": int((P.confidence == "medium").sum()),
              "hand": int((P.method == "hand").sum()), "gaz_both": int((P.method == "gaz-both").sum()), "gaz_anc": int((P.method == "gaz-anc").sum()),
              "gaz_mod": int((P.method == "gaz-mod").sum()), "high_pct": pc((P.confidence == "high").sum(), len(P)),
              "unmatched": len(U), "dropped_dev": int(U.reason.fillna("").str.startswith("dropped").sum()),
              "rejected": int(U.reason.fillna("").str.startswith("rejected").sum()),
              "ambiguous": int(U.reason.fillna("").str.contains("ambiguous|several").sum()),
              "settlements": int((P.ftype == "settlement").sum()), "coastal": int(P.ftype.isin(["cape", "mouth", "harbour"]).sum()),
              "europe": int((P.continent == "Europe").sum()), "africa": int((P.continent == "Africa").sum()), "asia": int((P.continent == "Asia").sum()),
              "pleiades": int((P.source == "Pleiades").sum()), "dare": int((P.source == "DARE").sum()), "ne": int((P.source == "Natural Earth").sum())}
R["match"]["india_east"] = int(((P.continent == "Asia") & (P.lon > 60)).sum())

# ---------- fits ----------
R["fit"] = {k: FIT[k] for k in ("f0", "f1", "f2", "f3", "f4", "shape_all")}
R["fit"]["b"] = B; R["fit"]["inv_b"] = round(1 / B, 2); R["fit"]["a"] = FIT["F1"]["a"]; R["fit"]["c"] = FIT["F1"]["c"]
R["fit"]["stadia_ratio"] = round(500 / 700, 3)
R["fit"]["b_vs_stadia_pct"] = round(100 * (B - 500 / 700) / (500 / 700), 1)
R["fit"]["helmert_scale"] = FIT["F3"]["scale"]; R["fit"]["helmert_rot"] = FIT["F3"]["rot_deg"]
R["fit"]["f0_to_f1_drop_pct"] = round(100 * (1 - FIT["f1"]["median_km"] / FIT["f0"]["median_km"]))
R["fit"]["f1_within_100_pct"] = pc((P.f1_km <= 100).sum(), len(P)); R["fit"]["f1_over_500_pct"] = pc((P.f1_km > 500).sum(), len(P))
R["fit"]["prime_meridian"] = round(-FIT["F1"]["a"] / 1, 2)          # where Ptolemy's 0 degrees falls in modern longitude, by F1
R["fit"]["prime_meridian_w"] = round(-FIT["F1"]["a"], 1)
for cont in ("Europe", "Africa", "Asia"):
    g = P[P.continent == cont]
    w = np.cos(g.lat * D2R)
    A = np.c_[np.ones(len(g)), g.lon_o] * w.values[:, None]
    (a_, b_), *_ = np.linalg.lstsq(A, g.lon.values * w.values, rcond=None)
    R["fit"]["b_" + cont.lower()] = round(float(b_), 3)

# ---------- the eastward stretch ----------
sv, kt, se = byid.loc["2.05.03.06"], byid.loc["7.03.03.07"], byid.loc["6.16.08.07"]
R["stretch"] = {"ptol_span": round(se.lon_o - sv.lon_o, 1), "true_span": round(se.lon - sv.lon, 1), "ratio": round((se.lon_o - sv.lon_o) / (se.lon - sv.lon), 2),
                "west": "Cape St Vincent", "east": "Sera Metropolis (Xi'an)", "west_lon_o": sv.lon_o, "east_lon_o": se.lon_o,
                "kattigara_lon_o": kt.lon_o, "kattigara_lat_o": kt.lat_o, "kattigara_lat": kt.lat, "kattigara_lat_err": round(kt.lat - kt.lat_o, 1),
                "kattigara_f1_km": round(kt.f1_km)}
slope, icpt = np.polyfit(P.dlon_true, P.dlon_ptol, 1)
R["stretch"]["slope_alex"] = round(float(slope), 2)
R["stretch"]["per10"] = round(float(slope) * 10, 1)
# where the stretch puts the far east if his degrees were real degrees
R["stretch"]["east_overshoot_deg"] = round((se.lon_o + FIT["alex_offset"]) - se.lon, 1)

# ---------- error and distance from Alexandria ----------
bins = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, 12000)]
R["alex_bins"] = []
for lo, hi in bins:
    g = P[(P.dist_alex_km >= lo) & (P.dist_alex_km < hi)]
    R["alex_bins"].append({"lo": lo, "hi": hi, "n": len(g), "f0_km": round(float(g.f0_km.median())), "f1_km": round(float(g.f1_km.median())),
                           "f0_pct": round(float((g.f0_km / g.dist_alex_km.clip(lower=50)).median() * 100))})
from scipy.stats import spearmanr
R["alex"] = {"spearman_f0": round(float(spearmanr(P.dist_alex_km, P.f0_km).correlation), 2), "spearman_f1": round(float(spearmanr(P.dist_alex_km, P.f1_km).correlation), 2),
             "near_f0": R["alex_bins"][0]["f0_km"], "far_f0": R["alex_bins"][-1]["f0_km"], "far_n": R["alex_bins"][-1]["n"],
             "f0_pct_all": round(float((P.f0_km / P.dist_alex_km.clip(lower=50)).median() * 100))}
for k, i in (("London", "2.03.27.02"), ("Rome", "3.01.61.02"), ("Cadiz", "2.04.16.03"), ("Jerusalem", "5.16.08.01"), ("Athens", "3.15.22.03"),
             ("Byzantium", "3.11.05.02"), ("Carthage", "4.03.07.01"), ("Babylon", "5.20.06.07"), ("Samarkand", "6.11.09.03"), ("Taxila", "7.01.45.05"),
             ("Patna", "7.01.73.03"), ("Xian", "6.16.08.07"), ("Kattigara", "7.03.03.07"), ("Marseille", "2.10.08.06"), ("Rhodes", "5.02.34.05"), ("Alexandria", ALEX),
             ("Prason", "4.08.02.01"), ("Komaria", "7.01.09.06"), ("Lyon", "2.08.17.06"), ("York", "2.03.17.01"), ("Antioch", "5.15.16.02")):
    r = byid.loc[i]
    R.setdefault("places", {})[k] = {"id": i, "lon_o": round(r.lon_o, 2), "lat_o": round(r.lat_o, 2), "lat": round(r.lat, 2), "lon": round(r.lon, 2),
                                     "f0_km": round(r.f0_km), "f1_km": round(r.f1_km), "dist_alex": round(r.dist_alex_km), "lat_err": round(r.lat_err, 1),
                                     "dlon_true": round(r.dlon_true, 1), "dlon_ptol": round(r.dlon_ptol, 1)}

# ---------- latitudes ----------
R["lat"] = {"median_abs": round(float(P.lat_err.abs().median()), 2), "within1_pct": pc((P.lat_err.abs() <= 1).sum(), len(P)),
            "mean_signed": round(float(P.lat_err.mean()), 2)}
for k, mp in (("britain", "EU01"), ("africa", "AF02"), ("mauretania", "AF01"), ("egypt", "AF03"), ("greece", "EU10"), ("italy", "EU06"), ("syria", "AS04")):
    R["lat"][k] = round(float(P[P["map"] == mp].lat_err.median()), 1)

# ---------- regions ----------
regs = []
for mp, g in P.groupby("map"):
    regs.append({"map": mp, "name": g.map_name.iloc[0], "continent": g.continent.iloc[0], "n": len(g), "f1_km": round(float(g.f1_km.median())),
                 "f4_km": None if g.f4_km.isna().all() else round(float(g.f4_km.median())),
                 "shape_km": None if g.shape_km.isna().all() else round(float(g.shape_km.median())),
                 "lat_err": round(float(g.lat_err.median()), 1), "f0_km": round(float(g.f0_km.median())),
                 "b": FIT["F4"].get(mp, {}).get("b"), "rot": FIT["shape"].get(mp, {}).get("rot_deg"), "scale": FIT["shape"].get(mp, {}).get("scale"),
                 "lon_c": round(float(g.lon.median()), 2), "lat_c": round(float(g.lat.median()), 2), "ranked": len(g) >= MIN_N})
RG = pd.DataFrame(regs).sort_values("map", key=lambda s: s.str[:2].map({"EU": 0, "AF": 1, "AS": 2}) * 100 + s.str[2:].astype(int))
RG.to_csv(f"{DATA}/regions.csv", index=False)
R["regions"] = {r["map"]: r for r in regs}
rk = RG[RG.ranked].sort_values("shape_km")
R["rank_shape"] = rk["map"].tolist(); R["rank_f1"] = RG[RG.ranked].sort_values("f1_km")["map"].tolist()
R["n_ranked"] = len(rk); R["min_n"] = MIN_N
R["n_unranked"] = int((~RG.ranked).sum())
G = R["regions"]

# ---------- Scotland turned east ----------
BR = P[P.id.str[:4] == "2.03"].copy()


def local_helmert(g):
    m0, p0 = g.lat.mean(), g.lat_o.mean()
    x = (g.lon - g.lon.mean()) * np.cos(m0 * D2R); y = g.lat - m0
    xp = (g.lon_o - g.lon_o.mean()) * np.cos(p0 * D2R); yp = g.lat_o - p0
    Z = (xp + 1j * yp).values; Wv = (x + 1j * y).values
    s = (np.conj(Z) @ Wv) / (np.conj(Z) @ Z)
    return float(np.degrees(np.angle(s))), float(abs(s))


rs, ss = local_helmert(BR[BR.lat >= 55.0]); re_, se_ = local_helmert(BR[BR.lat < 55.0])


def ptol_bearing(a, b):
    """Bearing from a to b on Ptolemy's map (his degrees, longitude times cos latitude), clockwise from north."""
    dx = (b.lon_o - a.lon_o) * np.cos((a.lat_o + b.lat_o) / 2 * D2R); dy = b.lat_o - a.lat_o
    return float((np.degrees(np.arctan2(dx, dy)) + 360) % 360)


so, du = byid.loc["2.03.02.08"], byid.loc["2.03.05.03"]
R["scotland"] = {"n_scot": int((BR.lat >= 55.0).sum()), "n_eng": int((BR.lat < 55.0).sum()), "rot_scot": round(rs, 1), "rot_eng": round(re_, 1),
                 "turn": round(rs - re_, 1), "scale_scot": round(ss, 2), "scale_eng": round(se_, 2), "brg_true": round(float(bearing(so.lat, so.lon, du.lat, du.lon))), "brg_ptol": round(ptol_bearing(so, du)),
                 "lat_err": G["EU01"]["lat_err"]}
R["scotland"]["brg_diff"] = R["scotland"]["brg_ptol"] - R["scotland"]["brg_true"]
R["scotland"]["dunnet_lat_o"] = round(byid.loc["2.03.01.13"].lat_o, 2); R["scotland"]["dunnet_lat"] = round(byid.loc["2.03.01.13"].lat, 2)
R["scotland"]["dunnet_lon_o"] = round(byid.loc["2.03.01.13"].lon_o, 2); R["scotland"]["london_lon_o"] = round(byid.loc["2.03.27.02"].lon_o, 2)

# ---------- India squashed, Taprobane swollen ----------
bg, km = byid.loc["7.01.62.04"], byid.loc["7.01.09.06"]
R["india"] = {"lat_span_true": round(bg.lat - km.lat, 1), "lat_span_ptol": round(bg.lat_o - km.lat_o, 1), "komaria_lat_o": km.lat_o, "komaria_lat": km.lat,
              "komaria_err": round(km.lat_o - km.lat, 1), "brg_true": round(float(bearing(bg.lat, bg.lon, km.lat, km.lon))), "brg_ptol": round(ptol_bearing(bg, km))}
R["india"]["ratio"] = round(R["india"]["lat_span_ptol"] / R["india"]["lat_span_true"], 2)
R["india"]["n"] = int((P["map"] == "AS10").sum())
# Ptolemy's Taprobane: the coast in sections 7.04.02 to 7.04.07, joined in his order, minus river sources
T = C[C.id.str.match(r"7\.04\.0[2-7]") & C.has_o & ~C.ftype.isin(["source", "river"])]
T = T[~T[["lon_o", "lat_o"]].duplicated()]
km_x = lambda lo, la: lo * B * np.cos(la * D2R) * 111.2
tp = Polygon(list(zip(km_x(T.lon_o.values, T.lat_o.values), T.lat_o.values * 111.2)))
EA = Transformer.from_crs(4326, 6933, always_xy=True)
lka = [f for f in W["features"] if f["properties"]["iso"] == "LKA"][0]
lka_area = stransform(EA.transform, shape(lka["geometry"])).area / 1e6
lka_lats = [c[1] for ring in (lka["geometry"]["coordinates"] if lka["geometry"]["type"] == "Polygon" else [p[0] for p in lka["geometry"]["coordinates"]]) for c in (ring if isinstance(ring[0][0], float) else ring[0])]
R["taprobane"] = {"n_coast": len(T), "lat_max_o": round(float(T.lat_o.max()), 2), "lat_min_o": round(float(T.lat_o.min()), 2),
                  "lat_span_o": round(float(T.lat_o.max() - T.lat_o.min()), 1), "area_ptol": round(tp.area), "area_true": round(lka_area),
                  "lat_max": round(max(lka_lats), 2), "lat_min": round(min(lka_lats), 2)}
R["taprobane"]["lat_span"] = round(R["taprobane"]["lat_max"] - R["taprobane"]["lat_min"], 1)
R["taprobane"]["area_ratio"] = round(tp.area / lka_area, 1); R["taprobane"]["span_ratio"] = round(R["taprobane"]["lat_span_o"] / R["taprobane"]["lat_span"], 1)
R["taprobane"]["equator_crossed"] = bool(T.lat_o.min() < 0)
ind = [f for f in W["features"] if f["properties"]["iso"] == "IND"][0]
R["taprobane"]["india_area"] = round(stransform(EA.transform, shape(ind["geometry"])).area / 1e6)
R["taprobane"]["pct_of_india_true"] = round(100 * lka_area / R["taprobane"]["india_area"], 1)
R["taprobane"]["n_matched"] = int((P["map"] == "AS12").sum())

# ---------- the Caspian, an enclosed sea ----------
CS = ["5.09.12.05", "5.09.12.03", "5.09.12.04", "5.12.02.03", "5.12.02.07", "5.12.01.07", "6.02.02.03", "6.14.02.04"]   # mouths on the real Caspian
cs = byid.loc[CS]
kx = lambda lo, la: lo * np.cos(np.radians(la.mean())) * 111.2
R["caspian"] = {"n": len(CS), "ns_true": round((cs.lat.max() - cs.lat.min()) * 111.2), "ns_ptol": round((cs.lat_o.max() - cs.lat_o.min()) * 111.2),
                "ew_true": round(float(kx(cs.lon.max() - cs.lon.min(), cs.lat))), "ew_ptol": round(float(kx(B * (cs.lon_o.max() - cs.lon_o.min()), cs.lat_o)))}
minx, miny, maxx, maxy = CASP.bounds
R["caspian"]["sea_ns"] = round((maxy - miny) * 111.2); R["caspian"]["sea_ew_max"] = round(max(
    (lambda seg: (seg.bounds[2] - seg.bounds[0]) * np.cos(np.radians(y)) * 111.2 if not seg.is_empty else 0)(CASP.intersection(Polygon([(minx - 1, y - .01), (maxx + 1, y - .01), (maxx + 1, y + .01), (minx - 1, y + .01)])))
    for y in np.arange(miny + .1, maxy, .1)))
R["caspian"]["ratio_true"] = round(R["caspian"]["ns_true"] / R["caspian"]["ew_true"], 1); R["caspian"]["ratio_ptol"] = round(R["caspian"]["ns_ptol"] / R["caspian"]["ew_ptol"], 1)
ox, ja = byid.loc["6.09.01.05"], byid.loc["6.14.02.05"]
from shapely.ops import nearest_points
for k, r in (("oxus", ox), ("jaxartes", ja)):
    p = Point(r.lon, r.lat); q = nearest_points(CASP.exterior, p)[0]
    R["caspian"][k + "_to_caspian_km"] = round(float(gc_km(r.lat, r.lon, q.y, q.x)), -1)
R["caspian"]["oxus_lon_o"] = ox.lon_o; R["caspian"]["jaxartes_lon_o"] = ja.lon_o

# ---------- the Indian Ocean closed ----------
pr = byid.loc["4.08.02.01"]
R["ocean"] = {"prason_lat_o": pr.lat_o, "prason_lon_o": pr.lon_o, "prason_lat": pr.lat, "prason_err_km": round(pr.f1_km), "kattigara_lat_o": kt.lat_o, "kattigara_lon_o": kt.lon_o,
              "kattigara_lat": kt.lat, "kattigara_err_km": round(kt.f1_km), "kattigara_south_deg": round(kt.lat - kt.lat_o, 1),
              "gap_lon_o": round(kt.lon_o - pr.lon_o), "gap_true": round(kt.lon - pr.lon)}
R["ocean"]["prason_south_deg"] = round(pr.lat - pr.lat_o, 1)

# ---------- the two recensions ----------
Bc = C[C.has_o & C.has_x].copy()
Bc["d_lon"] = (Bc.lon_o - Bc.lon_x).abs(); Bc["d_lat"] = (Bc.lat_o - Bc.lat_x).abs()
Bc["same"] = (Bc.d_lon < 1e-6) & (Bc.d_lat < 1e-6)
Bc["d_km"] = gc_km(Bc.lat_o, Bc.lon_o * B, Bc.lat_x, Bc.lon_x * B)
dif = Bc[~Bc.same]
R["rec"] = {"both": len(Bc), "same": int(Bc.same.sum()), "same_pct": pc(Bc.same.sum(), len(Bc)), "differ": len(dif), "differ_pct": pc(len(dif), len(Bc)),
            "lon_only": int(((dif.d_lon > 1e-6) & (dif.d_lat < 1e-6)).sum()), "lat_only": int(((dif.d_lon < 1e-6) & (dif.d_lat > 1e-6)).sum()),
            "median_diff_arcmin": round(float(np.maximum(dif.d_lon, dif.d_lat).median() * 60)), "median_diff_km": round(float(dif.d_km.median())),
            "over1deg": int((np.maximum(dif.d_lon, dif.d_lat) >= 1).sum()), "over5deg": int((np.maximum(dif.d_lon, dif.d_lat) >= 5).sum()),
            "omega_only": int((C.has_o & ~C.has_x).sum()), "xi_only": int((C.has_x & ~C.has_o).sum()),
            "fit_omega_km": FIT["rec_omega"]["median_km"], "fit_xi_km": FIT["rec_xi"]["median_km"], "fit_n": FIT["rec_omega"]["n"],
            "b_omega": FIT["rec_omega"]["b"], "b_xi": FIT["rec_xi"]["b"]}
pb = P[P.xi_km.notna()]
pbd = pb[(pb.lon_o != pb.lon_x) | (pb.lat_o != pb.lat_x)]
R["rec"]["places_differ"] = len(pbd); R["rec"]["omega_closer"] = int((pbd.f1_km < pbd.xi_km).sum()); R["rec"]["xi_closer"] = int((pbd.xi_km < pbd.f1_km).sum())
R["rec"]["omega_closer_pct"] = pc(R["rec"]["omega_closer"], len(pbd))
# fractions of a degree: Ptolemy writes minutes as fractions; which multiples of 5 minutes are used
mins = ((C.lon_o.dropna() % 1) * 60).round().astype(int) % 60
R["rec"]["fraction_5min_pct"] = pc((mins % 5 == 0).sum(), len(mins))
R["rec"]["whole_deg_pct"] = pc((mins == 0).sum(), len(mins))
# largest disagreement by book
book_d = dif.groupby(dif.id.str[0]).size().to_dict(); book_n = Bc.groupby(Bc.id.str[0]).size().to_dict()
R["rec"]["by_book"] = {k: {"n": int(book_n[k]), "differ": int(book_d.get(k, 0)), "pct": pc(book_d.get(k, 0), book_n[k])} for k in sorted(book_n)}

R["meta"] = {"page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "slug": SLUG, "cat_doi": CAT_DOI, "pleiades_version": PLEIADES_VER}

# ---------- page data ----------
MAPL = list(MAPS); CONTL = ["Europe", "Africa", "Asia"]
METH = ["gaz-both", "gaz-anc", "gaz-mod", "hand"]
nn = lambda v, k=3: None if pd.isna(v) else round(float(v), k)
pl_rows = []
for r in P.itertuples():
    pl_rows.append([r.id, r.locality.replace("*", ""), r.modern, MAPL.index(r.map), CONTL.index(r.continent), nn(r.lon_o), nn(r.lat_o), nn(r.lon_x), nn(r.lat_x),
                    nn(r.lat, 3), nn(r.lon, 3), nn(r.f1_lat, 2), nn(r.f1_lon, 2), int(round(r.f1_km)), int(round(r.f0_km)), None if pd.isna(r.shape_km) else int(round(r.shape_km)),
                    METH.index(r.method), 1 if r.confidence == "high" else 0, 1 if r.starred else 0, r.ftype, r.gtitle if isinstance(r.gtitle, str) else "",
                    r.region, 1 if r.modern_near else 0])
rest = C[(C.has_o | C.has_x) & ~C.id.isin(P.id)]
oth_rows = [[r.id, str(r.locality).replace("*", ""), r.modern if isinstance(r.modern, str) else "", nn(r.lon_o if not pd.isna(r.lon_o) else r.lon_x), nn(r.lat_o if not pd.isna(r.lat_o) else r.lat_x), r.ftype, MAPL.index(r.map)]
            for r in rest.itertuples()]
site = {"cols": ["id", "name", "modern", "map", "cont", "lon_o", "lat_o", "lon_x", "lat_x", "lat", "lon", "f1_lat", "f1_lon", "f1_km", "f0_km", "shape_km",
                 "meth", "high", "star", "ftype", "gaz", "region", "near"],
        "places": pl_rows, "other_cols": ["id", "name", "modern", "lon_o", "lat_o", "ftype", "map"], "other": oth_rows,
        "maps": [[k, MAPS[k]] for k in MAPL], "conts": CONTL, "methods": METH, "coasts": jload(f"{DATA}/coasts.json"),
        "regions": RG.replace({np.nan: None}).to_dict(orient="records"), "fit": {"a": FIT["F1"]["a"], "b": B, "c": FIT["F1"]["c"]},
        "alex": [ALEX_TRUE[0], ALEX_TRUE[1]], "caspian": jload(f"{DATA}/caspian.json")["geometry"]["coordinates"][0],
        "taprobane": [[nn(x, 2), nn(y, 2)] for x, y in zip(T.lon_o, T.lat_o)]}
mx = np.maximum(Bc.d_lon, Bc.d_lat) * 60
HB = [("identical", "same", mx < 1e-4), ("under 10 minutes", "<10'", (mx >= 1e-4) & (mx < 10)), ("10 to 30 minutes", "10-30'", (mx >= 10) & (mx < 30)),
      ("30 minutes to 1 degree", "30'-1°", (mx >= 30) & (mx < 60)), ("1 to 5 degrees", "1-5°", (mx >= 60) & (mx < 300)), ("5 degrees or more", "5°+", mx >= 300)]
site["rec_hist"] = [{"label": a, "short": b, "n": int(m.sum())} for a, b, m in HB]
assert sum(h["n"] for h in site["rec_hist"]) == len(Bc)
jsave(site, f"{DATA}/site.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("source", "match", "fit", "stretch", "alex", "lat", "scotland", "india", "taprobane", "caspian", "ocean", "rec")}, indent=0)[:6000])
print(RG.to_string())
