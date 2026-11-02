"""Geography: outlines for the page and figures (Natural Earth 1:50m), and a modern position for every catalogue entry
that the editors identified (Modern_location filled in) and that is a point: a settlement, cape, river mouth, island
or harbour. Entries without an identification are never matched: an uncertain match is worse than none.

Methods, in order of preference (the method and a confidence are recorded for every match):
  1. hand    My own coordinates for well-known coasts, river mouths, capes and cities (code/reading.py HAND), each
             checked against the editors' identification. Confidence 'high' (named landmarks) or 'medium'.
  2. gaz-both  A gazetteer place (Pleiades or DARE) inside the chapter's box whose ancient names include Ptolemy's
             name AND whose modern names include the editors' identification. Confidence 'high'.
  3. gaz-anc   A gazetteer place inside the box whose ancient names include Ptolemy's name, the only such place (all
             candidates within 25 km of each other). Confidence 'medium'.
  4. gaz-mod   A gazetteer or Natural Earth town inside the box whose modern name equals the editors' identification,
             the only such place. Confidence 'medium'.
Ancient names are compared on a skeleton that ignores Greek and Latin spelling (k/c, ou/u, ai/ae, os/us, final -a,
-e, -on, -um and so on); modern names on a skeleton that also ignores German transliteration (sch/sh, dsch/j, w/v).
Rough Pleiades locations are used only when a second source agrees. Matches that the editors mark 'bei' (near) keep
that flag. Places rejected after inspection (code/reading.py REJECT) are dropped here.
Outputs: data/world.json, data/caspian.json (the Caspian's shore from Natural Earth), data/matches.csv (one row per matched entry: id, modern lat, lon, method, confidence,
source, gazetteer id and title, distance between agreeing sources) and data/unmatched_points.csv."""
import difflib
import numpy as np, pandas as pd
from shapely.geometry import shape, mapping
from common import *
import reading

iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]


def rnd(c, k=2):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], k), round(c[1], k)]
    return [rnd(x, k) for x in c]


# ---------- outlines ----------
W50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
feats = []
for f in W50["features"]:
    gs = shape(f["geometry"]).simplify(0.03, preserve_topology=True)
    if gs.is_empty: continue
    gm = mapping(gs)
    feats.append({"type": "Feature", "properties": {"iso": iso_of(f["properties"]), "name": f["properties"].get("NAME_EN") or f["properties"]["NAME"]},
                  "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")
# the Caspian Sea: the hole in Natural Earth's 1:50m land polygon that contains 51 E, 42 N
from shapely.geometry import Point, Polygon
for f in jload(f"{GEO}/ne_50m_land.geojson")["features"]:
    g = shape(f["geometry"])
    for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        for ring in poly.interiors:
            if Polygon(ring).contains(Point(51, 42)):
                CASP = Polygon(ring).simplify(0.02)
jsave({"type": "Feature", "properties": {"name": "Caspian Sea"}, "geometry": {"type": "Polygon", "coordinates": rnd([list(CASP.exterior.coords)], 3)}}, f"{DATA}/caspian.json")


# ---------- name skeletons ----------
def sk(s):
    """Ancient-name skeleton: Greek and Latin spellings of the same name collapse to one key."""
    s = norm(s).replace(" ", "")
    for a, b in (("ph", "f"), ("th", "t"), ("ch", "c"), ("kh", "c"), ("k", "c"), ("q", "c"), ("y", "i"), ("ou", "u"), ("ae", "e"),
                 ("ai", "e"), ("oe", "e"), ("oi", "e"), ("ei", "i"), ("j", "i"), ("w", "u"), ("v", "u"), ("rh", "r"), ("z", "s"), ("x", "cs")):
        s = s.replace(a, b)
    s = re.sub(r"(.)\1+", r"\1", s)
    if len(s) > 5:
        s = re.sub(r"(ion|ium|eia|ia|on|um|os|us|es|is|as|e|a|i|o|u)$", "", s)
    return s


def mk(s):
    """Modern-name skeleton: also ignores German transliteration and a leading article."""
    s = norm(str(s).replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("Ä", "A").replace("Ö", "O").replace("Ü", "U"))
    s = re.sub(r"^(el|al|ed|es|er|ez|ash|as|at|ad|an|tell|tel|tall|khirbet|chirbet|kh|henchir|hr|ain|bir|kale|kalesi)\s+", "", s)
    s = re.sub(r"\s+(kale|kalesi|asari|harabeleri|hoyuk|huyuk|tepe|koy|koyu)$", "", s)
    s = s.replace(" ", "")
    for a, b in (("dsch", "j"), ("tsch", "c"), ("sch", "s"), ("sh", "s"), ("ch", "c"), ("kh", "c"), ("k", "c"), ("q", "c"), ("dh", "d"),
                 ("ph", "f"), ("th", "t"), ("w", "v"), ("ou", "u"), ("y", "i"), ("j", "i"), ("z", "s"), ("x", "cs")):
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)


def mod_match(a, b):
    if not a or not b or len(a) < 3 or len(b) < 3:
        return False
    if a == b:
        return True
    lo, hi = sorted((a, b), key=len)
    if len(lo) >= 6 and lo in hi and len(lo) >= .7 * len(hi):
        return True
    return len(lo) >= 7 and a[:2] == b[:2] and difflib.SequenceMatcher(None, a, b).ratio() >= .87


def modern_keys(m):
    """The editors' identification may name alternatives ('Capo Boeo oder Lilibeo') or a German exonym."""
    if not m:
        return []
    m = m.replace("Säule des Inneren Meeres", "")
    parts = re.split(r"\s+oder\s+|/|;|,|\(|\)|\s+bzw\.\s+", m)
    out = []
    for p in parts:
        p = re.sub(r"^(bei|nahe|am|an der|südlich von|nördlich von|östlich von|westlich von|Felsen v\.)\s+", "", p.strip()).strip(" ?.")
        if len(p) >= 3:
            out.append(p)
            if p in reading.EXONYM:
                out += reading.EXONYM[p]
    return [k for k in {mk(p) for p in out} if len(k) >= 3]


# ---------- gazetteers ----------
GZ = []          # dicts: src, gid, title, lat, lon, precise, anc (set of skeletons), mod (set of modern skeletons)
pl = pd.read_csv(f"{PLEIADES}/places.csv", dtype=str, keep_default_na=False)
nm = pd.read_csv(f"{PLEIADES}/names.csv", dtype=str, keep_default_na=False)
pl = pl[(pl.representative_latitude != "") & (pl.representative_longitude != "")]
# Pleiades place types: regions, rivers, peoples, mountains and seas are not settlements and never match one
PT = pd.read_csv(f"{PLEIADES_GIS}/places_place_types.csv", dtype=str).groupby("place_id").place_type.apply(set).to_dict()
NONPLACE = {"region", "river", "people", "mountain", "province", "province-2", "water-open", "lake", "road", "bay", "label", "aqueduct", "bridge", "canal", "wall-2", "wall"}
SETTLE = {"settlement", "fort", "fort-2", "station", "port", "fortified-settlement", "settlement-modern", "archaeological-site", "tell", "hillfort",
          "sanctuary", "temple", "temple-2", "island", "archipelago", "oppidum", "fortlet", "villa", "city-gate", "acropolis", "polis"}
pl = pl[[not (PT.get(i, set()) & NONPLACE) or bool(PT.get(i, set()) & SETTLE) for i in pl.id]]
ANC_LANG = {"", "la", "grc", "grc-Latn", "la-Latn", "egy", "akk", "hbo", "xpu", "phn", "arc", "peo", "pal", "sog", "bnt"}
anc, mod = {}, {}
for r in nm.itertuples():
    forms = {f for f in (r.attested_form, r.romanized_form_1, r.romanized_form_2, r.romanized_form_3) if f}
    for f in forms:
        for v in re.split(r"[,/;]", f):
            v = v.strip()
            if not v: continue
            if r.language_tag in ANC_LANG and r.name_type != "associated_modern":
                anc.setdefault(r.place_id, set()).add(sk(v))
            else:
                mod.setdefault(r.place_id, set()).add(mk(v))
for r in pl.itertuples():
    a = anc.setdefault(r.id, set())
    for v in re.split(r"[,/;]", re.sub(r"\([^)]*\)", "", r.title)):
        if v.strip(): a.add(sk(v))
    m = mod.setdefault(r.id, set())
    for paren in re.findall(r"\(([^)]*)\)", r.title):
        for v in re.split(r"[,/;?]| or ", paren):
            if v.strip(): m.add(mk(v))
    note = re.search(r"Directory notes: ([^<]*)", r.details)
    if note:
        for v in re.split(r"[,/;?]| or |\(|\)", note.group(1)):
            v = re.sub(r"\b(near|nr\.|area|vicinity|of|at|[A-Z]{3})\b", "", v).strip()
            if len(v) >= 3: m.add(mk(v))
    GZ.append({"src": "Pleiades", "gid": r.id, "title": r.title, "lat": float(r.representative_latitude), "lon": float(r.representative_longitude),
               "precise": r.location_precision == "precise", "anc": a, "mod": m})
n_pl = len(GZ)
for lev in ("high", "medium", "low"):
    for f in jload(f"{DARE}/places_{lev}.geojson")["features"]:
        p = f["properties"]; lon, lat = f["geometry"]["coordinates"][:2]
        a = {sk(v) for x in (p.get("latin") or "", p.get("greek") or "") for v in re.split(r"[,/;?]|\s+or\s+", x.replace("*", "")) if v.strip()}
        m = {mk(v) for v in re.split(r"[,/;?]|\(|\)", p.get("modern") or "") if v.strip()}
        GZ.append({"src": "DARE", "gid": p["id"], "title": (p.get("latin") or p.get("greek") or "") + (" / " + p["modern"] if p.get("modern") else ""),
                   "lat": lat, "lon": lon, "precise": (p.get("accuracy") or 9999) <= 1000, "anc": a, "mod": m})
for f in jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]:
    p = f["properties"]
    m = {mk(p["name"]), mk(p["nameascii"])} | ({mk(v) for v in str(p["namealt"]).split("|")} if p.get("namealt") else set())
    GZ.append({"src": "Natural Earth", "gid": str(p["ne_id"]), "title": p["name"], "lat": p["latitude"], "lon": p["longitude"], "precise": True, "anc": set(), "mod": m})
G = pd.DataFrame(GZ)
print("gazetteer records:", G.src.value_counts().to_dict())
GLAT, GLON = G.lat.values, G.lon.values
ANC_IDX, MOD_IDX = {}, {}
for i, g in enumerate(GZ):
    for k in g["anc"]:
        if len(k) >= 3: ANC_IDX.setdefault(k, []).append(i)
    for k in g["mod"]:
        if len(k) >= 3: MOD_IDX.setdefault(k, []).append(i)


def inbox(i, b):
    return b[0] <= GLON[i] <= b[2] and b[1] <= GLAT[i] <= b[3]


BOXKEYS = {}


def mod_cands(keys, b):
    """Gazetteer records in box b whose modern name matches one of the keys (exact, containment or close spelling)."""
    if b not in BOXKEYS:
        inb = np.where((GLON >= b[0]) & (GLON <= b[2]) & (GLAT >= b[1]) & (GLAT <= b[3]))[0]
        d = {}
        for i in inb:
            for k in GZ[i]["mod"]:
                if len(k) >= 3: d.setdefault(k, []).append(int(i))
        BOXKEYS[b] = d
    d = BOXKEYS[b]; out = set()
    for k in keys:
        for kk in d:
            if mod_match(k, kk):
                out |= set(d[kk])
    return out


def clusters(idx, r_km=25):
    idx = list(idx); cl = []
    for i in idx:
        for c in cl:
            if gc_km(GLAT[i], GLON[i], GLAT[c[0]], GLON[c[0]]) <= r_km:
                c.append(i); break
        else:
            cl.append([i])
    return cl


def best(c):
    """Representative point of a cluster: precise Pleiades first, then DARE, then Natural Earth."""
    order = {"Pleiades": 0, "DARE": 1, "Natural Earth": 2}
    return sorted(c, key=lambda i: (not GZ[i]["precise"], order[GZ[i]["src"]]))[0]


CAT = pd.DataFrame(jload(f"{WORK}/cat.json"))
PTS = CAT[CAT.ftype.isin(POINT_TYPES + ("harbour",)) & (CAT.has_o | CAT.has_x) & CAT.modern.notna()].copy()
rows, why = [], {}
for r in PTS.itertuples():
    b = CHAPTERS[r.ch][1]
    if r.id in reading.REJECT:
        why[r.id] = "rejected after inspection: " + reading.REJECT[r.id]; continue
    hk = r.id if r.id in reading.HAND else f"{r.ch}|{r.modern}"
    if hk in reading.HAND:
        lat, lon, conf = reading.HAND[hk]
        rows.append({"id": r.id, "lat": lat, "lon": lon, "method": "hand", "confidence": conf, "source": "author", "gid": "", "gtitle": "", "agree_km": None})
        continue
    if r.ftype not in ("settlement", "island", "harbour"):
        why[r.id] = "coastal or river feature without hand coordinates"; continue
    akeys = {sk(v) for v in r.variants if len(sk(v)) >= 3}
    mkeys = modern_keys(r.modern_clean)
    A = {i for k in akeys for i in ANC_IDX.get(k, []) if inbox(i, b)}
    M = mod_cands(mkeys, b)
    both = A & M
    if not both and A and M:     # ancient-name and modern-name records for the same place in different gazetteers
        near = {i for i in A for j in M if gc_km(GLAT[i], GLON[i], GLAT[j], GLON[j]) <= 12}
        both = near
    res = None
    if both:
        cl = clusters(both)
        if len(cl) == 1:
            i = best(cl[0]); oth = [gc_km(GLAT[i], GLON[i], GLAT[j], GLON[j]) for j in (A | M) if j != i and gc_km(GLAT[i], GLON[i], GLAT[j], GLON[j]) < 25]
            res = (i, "gaz-both", "high", max(oth) if oth else 0.0)
        else:
            why[r.id] = "ancient and modern names agree at several places"
    elif A:
        Ap = {i for i in A if GZ[i]["precise"]}
        cl = clusters(Ap) if Ap else []
        if len(cl) == 1:
            res = (best(cl[0]), "gaz-anc", "medium", None)
        else:
            why[r.id] = "ancient name ambiguous or rough in the region" if cl or A else "no gazetteer match"
    elif M:
        Mp = {i for i in M if GZ[i]["precise"]}
        cl = clusters(Mp) if Mp else []
        if len(cl) == 1:
            res = (best(cl[0]), "gaz-mod", "medium", None)
        else:
            why[r.id] = "modern name ambiguous in the region"
    else:
        why[r.id] = "no gazetteer match"
    if res:
        i, meth, conf, ag = res
        g = GZ[i]
        rows.append({"id": r.id, "lat": round(g["lat"], 5), "lon": round(g["lon"], 5), "method": meth, "confidence": conf, "source": g["src"],
                     "gid": g["gid"], "gtitle": g["title"], "agree_km": None if ag is None else round(ag, 1)})
M_ = pd.DataFrame(rows)
M_ = M_.merge(PTS[["id", "locality", "modern", "ch", "map", "ftype", "modern_near", "lon_o", "lat_o", "lon_x", "lat_x"]], on="id", how="left")

# ---------- consistency with neighbours ----------
# Ptolemy's errors are smooth: neighbouring places on his map are displaced together (all of Scotland is turned, all of
# India is squashed). A wrong identification shows up as a place displaced unlike its neighbours. For each match I fit,
# within its regional map, modern longitude as a linear function of Ptolemy's and modern latitude as Ptolemy's plus a
# constant, and compare its residual (km) with the median residual of its 8 nearest neighbours on Ptolemy's map.
# A 'medium' match (one name only) that departs by more than DEV_KM is dropped; 'high' and hand matches that do are
# kept but were inspected one by one (the ones I judged wrong are in reading.REJECT).
from scipy.spatial import cKDTree
DEV_KM = 300


def neighbour_dev(D):
    lp, bp = D.lon_o.fillna(D.lon_x).values, D.lat_o.fillna(D.lat_x).values
    px, py = np.full(len(D), np.nan), np.full(len(D), np.nan)
    for mp in D["map"].unique():
        ix = np.where(D["map"].values == mp)[0]
        if len(ix) < 5:
            continue
        b, a = np.polyfit(lp[ix], D.lon.values[ix], 1); c = np.median(D.lat.values[ix] - bp[ix])
        px[ix], py[ix] = a + b * lp[ix], c + bp[ix]
    rx = (px - D.lon.values) * np.cos(np.radians(D.lat.values)) * 111.2; ry = (py - D.lat.values) * 111.2
    T = cKDTree(np.c_[lp * np.cos(np.radians(bp)), bp])
    dev = []
    for i in range(len(D)):
        _, j = T.query([lp[i] * np.cos(np.radians(bp[i])), bp[i]], k=9)
        j = [x for x in j if x != i][:8]
        dev.append(float(np.hypot(rx[i] - np.nanmedian(rx[j]), ry[i] - np.nanmedian(ry[j]))))
    return np.array(dev)


for it in range(3):                      # repeat: a dropped bad match no longer pulls its neighbours
    M_["dev_km"] = neighbour_dev(M_).round(0)
    bad = (M_.confidence == "medium") & (M_.method != "hand") & (M_.dev_km > DEV_KM)
    for i in M_[bad].id:
        why[i] = f"dropped: one-name match displaced unlike its neighbours by more than {DEV_KM} km"
    M_ = M_[~bad].reset_index(drop=True)
M_ = M_.drop(columns=["lon_o", "lat_o", "lon_x", "lat_x"])
CHECK = M_[M_.dev_km > DEV_KM].sort_values("dev_km", ascending=False)
CHECK.to_csv(f"{WORK}/check_high.csv", index=False)
print(len(CHECK), "high or hand matches displaced unlike their neighbours (inspected; see reading.REJECT)")
M_.to_csv(f"{DATA}/matches.csv", index=False)
U = PTS[~PTS.id.isin(M_.id)][["id", "locality", "modern", "ch", "ftype"]].copy()
U["reason"] = U.id.map(why)
U.to_csv(f"{DATA}/unmatched_points.csv", index=False)
print(len(PTS), "identified point entries;", len(M_), "matched")
print(M_.groupby(["method", "confidence"]).size().to_string())
print(U.reason.value_counts().to_string())
