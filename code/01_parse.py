"""Read Grasshoff and Defaux's catalogue of Ptolemy's Geography (raw/PtolemyCatalogue.xlsx) and add what the later
steps need: the chapter (book.chapter), the region's English name, the regional map, a feature type parsed from the
German locality name, a starred flag (the catalogue marks Ptolemy's noteworthy cities with *), and the ancient name
variants used for gazetteer matching.

Feature types, by rule on the German name (first rule that applies):
  mouth      Muendung, Aestuar (river mouths and estuaries)
  source     Quelle(n)
  river      Biegung, Einmuendung, Zusammenfluss, Teilung, Kruemmung, Mitte, Lauf (points along a river)
  boundary   Grenzpunkt, Endpunkt, Grenze
  mountain   Gebirge, Berg, Berge, Alpen, Wald
  cape       Kap, Klippe, Vorgebirge, Spitze, Landspitze
  island     Insel(n)
  harbour    Hafen, Golf, Bucht (harbours and the heads of gulfs)
  lake       See, Sumpf
  settlement everything else with coordinates (towns, forts, villages)
Rows without coordinates in either recension (peoples, regions, seas) are kept in the catalogue file but play no part.
Output: data/catalogue.csv (all 10,049 rows, with the added columns) and WORK/cat.json."""
import numpy as np, pandas as pd
from common import *

X = pd.read_excel(f"{RAW}/PtolemyCatalogue.xlsx", dtype={"ID": str, "ID_map": str})
X.columns = ["id", "map", "locality", "modern", "lon_o", "lat_o", "lon_x", "lat_x"]
for c in ("locality", "modern"):
    X[c] = X[c].map(lambda s: re.sub(r"\s+", " ", str(s)).strip() if isinstance(s, str) else None)
X["ch"] = X.id.str[:4]
assert set(X.ch) <= set(CHAPTERS), set(X.ch) - set(CHAPTERS)
X["region"] = X.ch.map(lambda c: CHAPTERS[c][0])
X["map_name"] = X["map"].map(MAPS)
X["continent"] = X["map"].str[:2].map(CONT)
X["book"] = X.id.str[0].astype(int)
X["starred"] = X.locality.str.contains(r"\*", regex=True)
X["has_o"] = X.lon_o.notna() & X.lat_o.notna()
X["has_x"] = X.lon_x.notna() & X.lat_x.notna()

RULES = [("mouth", r"Mündung|Ästuar"), ("source", r"Quell"),
         ("river", r"Biegung|Einmündung|Zusammenfluss|Teilung|Krümmung|\(Mitte\)|Lauf\b|Oberlauf|Unterlauf|Aufteilung|Spaltung|Arm\b"),
         ("boundary", r"Grenzpunkt|Endpunkt|Grenze|Ostende|Westende|Nordende|Südende|-Ende\)"), ("mountain", r"Gebirge|Berg\b|Berge\b|-Berg|Alpen|Wald\b"),
         ("cape", r"^Kap\b|\bKap\b|Klippe|Vorgebirge|Spitze|Landspitze"), ("island", r"Insel"),
         ("harbour", r"Hafen|Golf|Bucht"), ("lake", r"\bSee\b|-See\b|Sumpf")]


def ftype(s):
    for t, rx in RULES:
        if re.search(rx, s):
            return t
    return "settlement"


X["ftype"] = X.locality.map(ftype)
X.loc[~(X.has_o | X.has_x), "ftype"] = "no coordinates"

STRIP = [r"-?Mündung\b.*$", r"-?Ästuar.*$", r"^Kap (der|des)?\s*", r"^Kap\b", r"-Insel\b", r"\bInsel\b", r"-Hafen\b", r"\bHafen der\b"]


def variants(loc):
    """Ancient name variants from a German locality string: alternatives in brackets, after 'bzw.', '/', ','."""
    s = loc.replace("*", "")
    s = re.sub(r"–>.*$", "", s)
    parts = re.split(r"\s+bzw\.\s+|/|,|\(|\)", s)
    out = []
    for p in parts:
        p = p.strip(" .:")
        if not p or re.match(r"^(Legio\b|Mitte\b|[NSOW]{1,2}\b|\d)", p):
            continue
        for rx in STRIP:
            p = re.sub(rx, "", p).strip()
        q = re.sub(r"\s+(am|an der|bei|von|vom|des|der|in|im)\s+.*$", "", p).strip()
        q2 = re.sub(r"^(Alt|Neu)-", "", q)
        for v in {p, q, q2, re.sub(r"\s+Metropolis$", "", q2)}:
            if len(v) >= 3 and not re.search(r"[a-zäöü]{3,}(Mündung|Quelle)", v):
                out.append(v)
    return sorted(set(out), key=len, reverse=True)


X["variants"] = X.locality.map(variants)
X["modern_clean"] = X.modern.map(lambda m: None if not isinstance(m, str) else re.sub(r"^(bei|nahe|am|an der|südlich von|nördlich von|östlich von|westlich von)\s+", "", m).strip())
X["modern_near"] = X.modern.fillna("").str.match(r"^(bei|nahe|am |an der|südlich|nördlich|östlich|westlich)")

# checks on the reading
a = X.set_index("id")
assert a.loc[ALEX, "locality"].startswith("Alexandreia") and a.loc[ALEX, "lon_o"] == 60.5 and a.loc[ALEX, "lat_o"] == 31
assert a.loc["7.01.09.06", "ftype"] == "cape" and a.loc["2.03.06.11", "ftype"] == "mouth" and a.loc["2.03.17.01", "ftype"] == "settlement"
print(len(X), "rows;", int((X.has_o | X.has_x).sum()), "with coordinates;", int(X.has_o.sum()), "Omega;", int(X.has_x.sum()), "Xi")
print(X[X.has_o | X.has_x].ftype.value_counts().to_string())
out = X.drop(columns=["variants"]).copy()
out["variants"] = X.variants.map(lambda v: "; ".join(v))
out.to_csv(f"{DATA}/catalogue.csv", index=False)
jsave(X.replace({np.nan: None}).to_dict(orient="records"), f"{WORK}/cat.json")
