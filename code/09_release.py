"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23882603, https://doi.org/10.5281/zenodo.23882603 and https://blog.tristanhotham.com/2026/10/31/ptolemy/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Ptolemy"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
G = R["regions"]

# numbers written in words or alt text in the blog and collage
assert round(R["stretch"]["slope_alex"], 2) == 1.37
assert R["alex_bins"][0]["f0_km"] == 134 and R["alex_bins"][-1]["f0_km"] > 1400
assert all(100 <= b["f1_km"] <= 220 for b in R["alex_bins"][:-1]) and 600 <= R["alex_bins"][-1]["f1_km"] <= 700   # "100 to 220 km ... about 650 km"
assert (G["EU01"]["shape_km"], G["AF04"]["shape_km"], G["AS10"]["shape_km"]) == (128, 448, 528)
assert 40 <= G["EU07"]["shape_km"] <= 52 and 40 <= G["EU10"]["shape_km"] <= 52       # "around 40 to 50 km"

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Ptolemy's world, measured",
        "slug": "ptolemy",
        "excerpt": f"Ptolemy wrote the ancient world down as a table of coordinates. I matched {R['match']['places']:,} of his places to where they really are: shrink his longitudes by {R['fit']['b']:.2f} and the map falls into place, but Scotland is still turned on its side and Sri Lanka is {R['taprobane']['area_ratio']:.0f} times too big.",
        "seo_description": f"Ptolemy's Geography (about AD 150) set against a modern map: {R['match']['places']:,} places, the stretch in longitude, Scotland, India and Taprobane.",
        "tags": ["maps", "history", "Ptolemy", "ancient geography", "cartography", "data visualisation", "Roman Empire", "Alexandria"],
        "header_alt": f"Title card reading 'Ptolemy's World' in black and red on pale paper, beside a grid of Ptolemy's degrees dotted with thousands of coloured places and brown coastlines, and a small modern map with his coasts shrunk to fit. Text: {R['match']['places']:,} places, longitudes times {R['fit']['b']:.2f}, Sri Lanka {R['taprobane']['area_ratio']:.0f} times too big."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/ptolemy_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"ptolemy/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"ptolemy/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "ptolemy/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("\\textit{Geography}", "Geography").replace("$b$", "b")
zmeta = {"title": "Ptolemy's World, Measured: The Coordinates of the Geography Set Against a Modern Map",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p><p>Sources: Grasshoff and Defaux (2019), Catalog of Ptolemy's Geography, doi:10.5281/zenodo.3585758 (CC BY 4.0); Pleiades (CC BY 3.0); Digital Atlas of the Roman Empire (CC BY-SA); Natural Earth.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["Ptolemy", "Geography", "ancient cartography", "historical geography", "map distortion", "Pleiades", "Roman Empire", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.5281/zenodo.3585758", "relation": "isDerivedFrom", "resource_type": "dataset", "scheme": "doi"},
                                 {"identifier": "https://pleiades.stoa.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
