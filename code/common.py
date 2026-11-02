"""Shared paths, groupings and helpers for the ptolemy project.

Raw inputs (raw/ and local gazetteers, read in place, never modified; steps 03 onward and the release run without them):
  raw/PtolemyCatalogue.xlsx
      Grasshoff, G. and Defaux, O. (2019) Catalog of Ptolemy's Geography, main books. Zenodo,
      doi:10.5281/zenodo.3585758. CC BY 4.0. 10,049 rows: ID (book.chapter.section.entry), ID_map (Ptolemy's regional
      map), Locality (German), Modern_location (German, the editors' identification, blank when unknown), and longitude
      and latitude in the Omega and Xi recensions, in degrees east of the Fortunate Isles and north of the equator.
  /home/claude/rawstore/mappa-mundi/pleiades/places.csv, names.csv
      Pleiades, a gazetteer of past places (pleiades.stoa.org), version 4.1. CC BY 3.0.
  /home/claude/work/roman-roads/ext/pleiades.datasets/data/gis/places_place_types.csv  Pleiades place types (CC BY 3.0).
  /home/claude/work/roman-roads/ext/roman-empire/data/places_*.geojson, 10m_rivers_lake_centerlines.geojson
      Digital Atlas of the Roman Empire (DARE, J. Ahlfeldt, dare.ht.lu.se) as packaged by the Klokan Technologies
      roman-empire vector map. CC BY-SA.
  /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson, ne_10m_populated_places_simple.geojson
      Natural Earth (public domain).
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("PT_RAW", os.path.join(ROOT, "raw"))
PLEIADES = os.environ.get("PT_PLEIADES", "/home/claude/rawstore/mappa-mundi/pleiades")
PLEIADES_GIS = os.environ.get("PT_PLEIADES_GIS", "/home/claude/work/roman-roads/ext/pleiades.datasets/data/gis")
DARE = os.environ.get("PT_DARE", "/home/claude/work/roman-roads/ext/roman-empire/data")
GEO = os.environ.get("PT_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("PT_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("PTTMP", "/dev/shm/ptolemy"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "ptolemy"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23882603"                 # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/ptolemy/"           # filled in by the publisher
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
CAT_DOI = "10.5281/zenodo.3585758"
CAT_REF = ("Grasshoff, G. and Defaux, O. (2019) Catalog of Ptolemy's Geography, main books. Zenodo. "
           "https://doi.org/10.5281/zenodo.3585758")
PLEIADES_VER = "4.1"

# Ptolemy's chapters (book.chapter): English name, regional map, and a generous modern box (lon0, lat0, lon1, lat1)
# inside which a gazetteer match for a place in that chapter must fall. Boxes are wide on purpose: they only stop a
# name matching a namesake in another part of the world; they do not constrain how wrong Ptolemy may be.
CHAPTERS = {
    "2.02": ("Hibernia (Ireland)", (-11, 51, -5, 55.7)), "2.03": ("Albion (Britain)", (-8, 49.8, 2.2, 59.5)),
    "2.04": ("Baetica", (-7.7, 35.8, -1.2, 39)), "2.05": ("Lusitania", (-9.7, 36.8, -4.5, 42.3)),
    "2.06": ("Tarraconensis", (-9.5, 36.5, 4.5, 44)), "2.07": ("Aquitania", (-2, 42.5, 4.5, 47.8)),
    "2.08": ("Lugdunensis", (-5, 45.3, 5.5, 50.2)), "2.09": ("Belgica", (-1, 45.5, 9, 52.6)),
    "2.10": ("Narbonensis", (0.5, 42.3, 8, 46.6)), "2.11": ("Germania Magna", (3.5, 47, 24.5, 58.5)),
    "2.12": ("Raetia and Vindelicia", (6, 45.5, 13.5, 49.6)), "2.13": ("Noricum", (11.5, 45.8, 17.2, 48.9)),
    "2.14": ("Upper Pannonia", (13.5, 44.6, 19.2, 48.5)), "2.15": ("Lower Pannonia", (15.5, 44.2, 21.2, 48.3)),
    "2.16": ("Illyria and Dalmatia", (13, 40.5, 22.2, 46.6)),
    "3.01": ("Italy", (6.5, 37.8, 18.8, 47.2)), "3.02": ("Corsica", (8.3, 41.2, 9.8, 43.2)),
    "3.03": ("Sardinia", (7.9, 38.7, 10, 41.4)), "3.04": ("Sicily", (11.8, 36.4, 15.8, 38.9)),
    "3.05": ("European Sarmatia", (18, 43.5, 45, 62)), "3.06": ("Taurica (Crimea)", (32, 44, 37, 46.6)),
    "3.07": ("Iazyges Metanastae", (18.5, 45, 22.5, 48.6)), "3.08": ("Dacia", (20, 43.5, 30.5, 49)),
    "3.09": ("Upper Moesia", (18.5, 41.5, 24.2, 45.5)), "3.10": ("Lower Moesia", (22, 41.5, 33, 47.6)),
    "3.11": ("Thrace", (22.5, 40.2, 30, 43.6)), "3.12": ("Thracian Chersonese", (25.8, 39.9, 27.3, 40.9)),
    "3.13": ("Macedonia", (18.8, 38.2, 25.5, 42.7)), "3.14": ("Epirus", (19, 37.4, 22.6, 40.8)),
    "3.15": ("Achaia", (20.5, 36.3, 27, 39.3)), "3.16": ("Peloponnese", (20.5, 36.2, 23.7, 38.5)),
    "3.17": ("Crete", (23.3, 34.6, 26.6, 35.9)),
    "4.01": ("Mauretania Tingitana", (-10.5, 29.5, -1.5, 36.2)), "4.02": ("Mauretania Caesariensis", (-2.6, 33, 6.2, 37.2)),
    "4.03": ("Africa", (5, 29, 20, 37.7)), "4.04": ("Cyrenaica", (17, 28, 25.6, 33.2)),
    "4.05": ("Marmarica and Egypt", (21, 21, 37, 33)), "4.06": ("Inner Libya", (-18, 5, 25, 37)),
    "4.07": ("Ethiopia below Egypt", (24, -2, 52, 25)), "4.08": ("Inner Ethiopia", (20, -20, 52, 12)),
    "5.01": ("Pontus and Bithynia", (28.5, 39.5, 35.2, 42.3)), "5.02": ("Asia", (25.5, 36.3, 32.6, 41.6)),
    "5.03": ("Lycia", (28.5, 35.8, 31, 37.4)), "5.04": ("Galatia", (29.5, 37, 36.6, 42.3)),
    "5.05": ("Pamphylia", (29.5, 36.2, 33, 38.6)), "5.06": ("Cappadocia", (32.5, 36.8, 42.2, 41.7)),
    "5.07": ("Lesser Armenia", (36, 37.5, 41.6, 41)), "5.08": ("Cilicia", (32, 36, 37, 38.2)),
    "5.09": ("Asiatic Sarmatia", (35, 40, 55, 60)), "5.10": ("Colchis", (39.5, 41, 43, 43.7)),
    "5.11": ("Iberia (Caucasus)", (42, 41, 46.6, 43)), "5.12": ("Albania (Caucasus)", (44.5, 39.5, 50.6, 44.2)),
    "5.13": ("Greater Armenia", (38, 37, 50, 42)), "5.14": ("Cyprus", (32, 34.4, 34.8, 35.8)),
    "5.15": ("Syria", (34.5, 31.5, 40, 37.6)), "5.16": ("Judaea", (34, 29.5, 36, 33.6)),
    "5.17": ("Arabia Petraea", (32, 27.5, 37.6, 32.6)), "5.18": ("Mesopotamia", (37.5, 32.5, 45, 38.3)),
    "5.19": ("Arabia Deserta", (36, 27, 48, 35.2)), "5.20": ("Babylonia", (42.5, 29.5, 48.6, 34.6)),
    "6.01": ("Assyria", (41, 33, 47, 38.2)), "6.02": ("Media", (44, 32, 54.5, 40)),
    "6.03": ("Susiana", (46.5, 29, 51.2, 33.6)), "6.04": ("Persis", (49, 26, 57, 32.6)),
    "6.05": ("Parthia", (51, 33, 62, 39)), "6.06": ("Carmania Deserta", (54, 28, 62, 34)),
    "6.07": ("Arabia Felix", (34, 12, 60, 31)), "6.08": ("Carmania", (54, 24, 63, 31)),
    "6.09": ("Hyrcania", (51, 35, 62, 46)), "6.10": ("Margiana", (58, 35, 66, 40)),
    "6.11": ("Bactria", (62, 34, 72, 40)), "6.12": ("Sogdiana", (58, 37, 75, 47)),
    "6.13": ("Sacae", (68, 35, 80, 42)), "6.14": ("Scythia within Imaus", (45, 37, 90, 60)),
    "6.15": ("Scythia beyond Imaus", (70, 30, 110, 55)), "6.16": ("Serica", (70, 25, 115, 45)),
    "6.17": ("Aria", (58, 31, 66, 36.6)), "6.18": ("Paropanisadae", (66, 32.5, 72, 36)),
    "6.19": ("Drangiana", (59, 28, 65, 33)), "6.20": ("Arachosia", (63, 28, 72, 34)),
    "6.21": ("Gedrosia", (58, 24, 68, 30)),
    "7.01": ("India within the Ganges", (60, 6, 92, 37)), "7.02": ("India beyond the Ganges", (85, -5, 112, 30)),
    "7.03": ("Land of the Sinae", (95, -5, 115, 30)), "7.04": ("Taprobane (Sri Lanka)", (79, 5.5, 82.3, 10)),
}

# Ptolemy's 26 regional maps (Book 8), the unit for 'which regions are best and worst'
MAPS = {
    "EU01": "British Isles", "EU02": "Iberia", "EU03": "Gaul", "EU04": "Germany", "EU05": "Alps and Danube",
    "EU06": "Italy and Corsica", "EU07": "Sardinia and Sicily", "EU08": "Sarmatia and Crimea", "EU09": "Dacia, Moesia, Thrace",
    "EU10": "Greece", "AF01": "Mauretania", "AF02": "Roman Africa", "AF03": "Cyrenaica and Egypt", "AF04": "Inner Libya and Ethiopia",
    "AS01": "Asia Minor", "AS02": "Asiatic Sarmatia", "AS03": "Caucasus and Armenia", "AS04": "Cyprus, Syria, Mesopotamia",
    "AS05": "Media and Persia", "AS06": "Arabia", "AS07": "Central Asia", "AS08": "Scythia and Serica",
    "AS09": "Afghanistan and Gedrosia", "AS10": "India", "AS11": "Further India and China", "AS12": "Taprobane",
}
CONT = {"EU": "Europe", "AF": "Africa", "AS": "Asia"}
CONT_COL = {"Europe": "#2F5FA7", "Africa": "#B07A12", "Asia": "#B23A2A"}

# Places used as fixed points in the text (catalogue IDs, checked in 01_parse.py)
ALEX = "4.05.09.03"            # Alexandria, where Ptolemy worked
ALEX_TRUE = (31.1980, 29.9097)

# Feature types parsed from the German locality name (see 01_parse.py). Only point-like types enter the analysis.
POINT_TYPES = ("settlement", "cape", "mouth", "island", "harbour")


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).replace("ß", "ss"))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "k": return f"{float(v) / 1000:.1f}"
    raise ValueError(f)


def gc_km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))


def bearing(lat1, lon1, lat2, lon2):
    """Initial great-circle bearing from point 1 to point 2, degrees clockwise from north."""
    import numpy as np
    p1, p2, dl = np.radians(lat1), np.radians(lat2), np.radians(lon2 - lon1)
    x = np.sin(dl) * np.cos(p2); y = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360
