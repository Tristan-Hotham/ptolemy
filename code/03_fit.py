"""Fit Ptolemy's coordinates to the real world. Reads only data/ (raw/ is not needed from here on).

The analysis set: every matched point (data/matches.csv) with an Omega position, one row per real place (where the
same place appears twice, for example a river mouth that ends one chapter and starts the next, the first entry is
kept). Positions in the Xi recension are carried for the comparison of the two.

Transforms from Ptolemy's (longitude east of the Fortunate Isles, latitude) to modern (longitude, latitude), each
fitted by least squares with errors measured on the ground (longitude differences weighted by the cosine of latitude):
  F0  as written     Ptolemy's longitudes shifted so that Alexandria, where he worked, falls in the right place;
                     latitudes as written. No fitting at all: the map exactly as he drew it.
  F1  stretch        modern lon = a + b x Ptolemy lon; modern lat = c + Ptolemy lat (3 parameters). b measures how
                     much his degrees of longitude must be shrunk.
  F2  affine         modern lon and lat each a linear function of Ptolemy's lon and lat (6 parameters).
  F3  Helmert        a rotation, one scale and a shift of Ptolemy's grid (drawn with his own parallel of Rhodes,
                     36 degrees, as the map's aspect) onto the modern grid drawn the same way (4 parameters).
  F4  by region      F1 fitted separately for each of Ptolemy's 26 regional maps (3 parameters each).
  shape              F3 fitted separately for each regional map in local kilometres: what is left is the error in
                     the shape of the region, however it is placed, turned and scaled.
Residual = great-circle distance between the real place and where the transform puts Ptolemy's coordinates.
Outputs: data/places.csv, data/fit.json, data/coasts.json (Ptolemy's coasts: his coastal sections joined in the order
he lists them)."""
import numpy as np, pandas as pd
from common import *

C = pd.read_csv(f"{DATA}/catalogue.csv", dtype={"id": str, "ch": str, "map": str})
C["ch"] = C.id.str[:4]
M = pd.read_csv(f"{DATA}/matches.csv", dtype={"id": str})
P = M.merge(C[["id", "lon_o", "lat_o", "lon_x", "lat_x", "region", "map_name", "continent", "starred", "book"]], on="id", how="left")
P["sec"] = P.id.str[:7]
n_matched = len(P)
P = P[P.lon_o.notna()].copy()
n_omega = len(P)
P = P.sort_values("id")
P["key"] = P.lat.round(2).astype(str) + "," + P.lon.round(2).astype(str)
P = P[~P.key.duplicated()].drop(columns="key").reset_index(drop=True)
print(n_matched, "matched;", n_omega, "with Omega positions;", len(P), "distinct real places")
D2R = np.pi / 180


def resid(lon_hat, lat_hat, lon, lat):
    return gc_km(lat, lon, lat_hat, lon_hat)


def fit_stretch(lp, bp, lon, lat):
    """F1: lon = a + b lp (weighted by cos lat), lat = c + bp."""
    w = np.cos(lat * D2R)
    A = np.c_[np.ones_like(lp), lp] * w[:, None]
    (a, b), *_ = np.linalg.lstsq(A, lon * w, rcond=None)
    c = float(np.mean(lat - bp))
    return float(a), float(b), c


def fit_affine(lp, bp, lon, lat):
    w = np.cos(lat * D2R)
    A = np.c_[np.ones_like(lp), lp, bp]
    cx, *_ = np.linalg.lstsq(A * w[:, None], lon * w, rcond=None)
    cy, *_ = np.linalg.lstsq(A, lat, rcond=None)
    return cx, cy


K36 = np.cos(36 * D2R)


def helmert(xp, yp, x, y):
    """Similarity transform (complex least squares) from (xp, yp) to (x, y)."""
    Z = xp + 1j * yp; W = x + 1j * y
    Zc, Wc = Z - Z.mean(), W - W.mean()
    s = (np.conj(Zc) @ Wc) / (np.conj(Zc) @ Zc)
    t = W.mean() - s * Z.mean()
    return s, t


lp, bp, lon, lat = P.lon_o.values, P.lat_o.values, P.lon.values, P.lat.values
FIT = {"n": len(P)}
# F0: as written, aligned on Alexandria
CA = C.set_index("id").loc[ALEX]
off0 = ALEX_TRUE[1] - CA.lon_o
P["f0_lon"], P["f0_lat"] = lp + off0, bp
# F1
a, b, c = fit_stretch(lp, bp, lon, lat)
P["f1_lon"], P["f1_lat"] = a + b * lp, bp + c
FIT["F1"] = {"a": round(a, 3), "b": round(b, 4), "c": round(c, 3)}
# F2
cx, cy = fit_affine(lp, bp, lon, lat)
P["f2_lon"] = cx[0] + cx[1] * lp + cx[2] * bp; P["f2_lat"] = cy[0] + cy[1] * lp + cy[2] * bp
FIT["F2"] = {"lon": [round(float(v), 4) for v in cx], "lat": [round(float(v), 4) for v in cy]}
# F3
s, t = helmert(lp * K36, bp, lon * K36, lat)
W3 = s * (lp * K36 + 1j * bp) + t
P["f3_lon"], P["f3_lat"] = W3.real / K36, W3.imag
FIT["F3"] = {"scale": round(float(abs(s)), 4), "rot_deg": round(float(np.degrees(np.angle(s))), 2)}
# F4 by regional map
P["f4_lon"], P["f4_lat"] = np.nan, np.nan
FIT["F4"] = {}
for mp, g in P.groupby("map"):
    if len(g) < 8:
        continue
    a4, b4, c4 = fit_stretch(g.lon_o.values, g.lat_o.values, g.lon.values, g.lat.values)
    P.loc[g.index, "f4_lon"] = a4 + b4 * g.lon_o; P.loc[g.index, "f4_lat"] = g.lat_o + c4
    FIT["F4"][mp] = {"a": round(a4, 3), "b": round(b4, 4), "c": round(c4, 3), "n": len(g)}
# shape: local Helmert per regional map, in kilometres about the region's centre
P["shape_km"] = np.nan
FIT["shape"] = {}
for mp, g in P.groupby("map"):
    if len(g) < 8:
        continue
    m0, p0 = g.lat.mean(), g.lat_o.mean()
    x = (g.lon - g.lon.mean()) * np.cos(m0 * D2R) * 111.2; y = (g.lat - m0) * 111.2
    xp = (g.lon_o - g.lon_o.mean()) * np.cos(p0 * D2R) * 111.2; yp = (g.lat_o - p0) * 111.2
    s5, t5 = helmert(xp.values, yp.values, x.values, y.values)
    Wh = s5 * (xp.values + 1j * yp.values) + t5
    P.loc[g.index, "shape_km"] = np.abs(Wh - (x.values + 1j * y.values))
    FIT["shape"][mp] = {"scale": round(float(abs(s5)), 3), "rot_deg": round(float(np.degrees(np.angle(s5))), 1), "n": len(g)}
for k in ("f0", "f1", "f2", "f3", "f4"):
    P[k + "_km"] = resid(P[k + "_lon"], P[k + "_lat"], P.lon, P.lat)
    ok = P[k + "_km"].notna()
    FIT[k] = {"median_km": round(float(P.loc[ok, k + "_km"].median())), "rms_km": round(float(np.sqrt((P.loc[ok, k + "_km"] ** 2).mean()))),
              "p90_km": round(float(P.loc[ok, k + "_km"].quantile(.9))), "n": int(ok.sum())}
FIT["shape_all"] = {"median_km": round(float(P.shape_km.median())), "n": int(P.shape_km.notna().sum())}
# the Xi recension, fitted the same way on the places that have both
both = P[P.lon_x.notna()].copy()
for rec, lo, la in (("omega", "lon_o", "lat_o"), ("xi", "lon_x", "lat_x")):
    a_, b_, c_ = fit_stretch(both[lo].values, both[la].values, both.lon.values, both.lat.values)
    both[rec + "_km"] = resid(a_ + b_ * both[lo], both[la] + c_, both.lon, both.lat)
    FIT["rec_" + rec] = {"b": round(b_, 4), "median_km": round(float(both[rec + "_km"].median())), "n": len(both)}
P = P.merge(both[["id", "xi_km"]], on="id", how="left")
P["dist_alex_km"] = gc_km(ALEX_TRUE[0], ALEX_TRUE[1], P.lat, P.lon)
P["dlon_true"] = P.lon - ALEX_TRUE[1]
P["dlon_ptol"] = P.lon_o - CA.lon_o
P["lat_err"] = P.lat_o - P.lat                     # Ptolemy's latitude minus the real one (positive: too far north)
cols = ["id", "locality", "modern", "region", "ch", "map", "map_name", "continent", "ftype", "starred", "method", "confidence", "source", "gid", "gtitle",
        "modern_near", "lon_o", "lat_o", "lon_x", "lat_x", "lat", "lon", "dist_alex_km", "dlon_true", "dlon_ptol", "lat_err",
        "f0_km", "f1_lon", "f1_lat", "f1_km", "f2_km", "f3_km", "f4_km", "shape_km", "xi_km", "dev_km"]
P[cols].round({"f1_lon": 3, "f1_lat": 3, "f0_km": 0, "f1_km": 0, "f2_km": 0, "f3_km": 0, "f4_km": 0, "shape_km": 0, "xi_km": 0, "dist_alex_km": 0,
               "dlon_true": 3, "dlon_ptol": 3, "lat_err": 3}).to_csv(f"{DATA}/places.csv", index=False)
FIT.update({"n_matched": n_matched, "n_omega": n_omega, "alex_offset": round(float(off0), 3)})
jsave(FIT, f"{DATA}/fit.json", indent=1)
print(json.dumps({k: FIT[k] for k in ("F1", "F3", "f0", "f1", "f2", "f3", "f4", "shape_all", "rec_omega", "rec_xi")}, indent=0))

# ---------- Ptolemy's coasts ----------
# A section is coastal when at least 30% of its entries with coordinates are capes, river mouths or harbours (his
# coastal descriptions read as a tour along the shore). Its points, minus river sources and points along rivers,
# are joined in the order he lists them. Sections of islands (all island entries) are left out.
C["sec"] = C.id.str[:7]
X = C[C.has_o == True].copy()
coasts = []
for sec, g in X.groupby("sec", sort=True):
    if g.ftype.isin(["mouth", "cape", "harbour"]).mean() < .3 and sec not in ("6.02.02",):   # 6.02.02: the Median shore of the Caspian
        continue
    g = g[~g.ftype.isin(["source", "river", "mountain", "lake"])]
    if len(g) < 3:
        continue
    coasts.append({"sec": sec, "map": g["map"].iloc[0], "pts": [[round(float(x), 3), round(float(y), 3)] for x, y in zip(g.lon_o, g.lat_o)]})
jsave(coasts, f"{DATA}/coasts.json")
print(len(coasts), "coastal sections")
