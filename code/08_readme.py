"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, m, f, g = R["source"], R["match"], R["fit"], R["regions"]
sc, ind, tp, cs, rc = R["scotland"], R["india"], R["taprobane"], R["caspian"], R["rec"]
N = lambda v: f"{round(v):,}"
readme = f"""# Ptolemy's world, measured

The coordinates of Ptolemy's Geography (about AD 150) set against a modern map: {N(m['places'])} of his places matched to where they really are, the stretch in his longitudes, how the error grows with distance from Alexandria, Scotland turned east, India flattened and Taprobane swollen, the Caspian and the Indian Ocean as closed seas, the best and worst of his 26 regional maps, and how far the Omega and Xi recensions differ.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- Source: {N(s['rows'])} catalogue entries, {N(s['with_coords'])} with coordinates ({N(s['omega'])} Omega, {N(s['xi'])} Xi). Of {N(s['points'])} point features (towns, capes, river mouths, harbours, islands) with coordinates, the editors identify {N(s['points_identified'])} ({s['identified_pct']:.0f}%).
- Matching: {N(m['matched'])} identified points matched ({m['pct_of_identified']:.0f}%), {N(m['places'])} distinct places: {m['gaz_both']} where a gazetteer's ancient and modern names both agree (high), {m['gaz_anc']} by ancient name and {m['gaz_mod']} by modern name alone (medium), {m['hand']} by hand (capes, river mouths, eastern cities). {m['high_pct']:.0f}% high confidence. Europe {m['europe']}, Africa {m['africa']}, Asia {m['asia']}.
- The stretch: real longitude = {f['a']:.2f} + {f['b']:.4f} x Ptolemy's. 500/700 = {f['stadia_ratio']:.3f}, the ratio implied by his 500-stadia degree. Every 10 degrees of real longitude from Alexandria is {R['stretch']['per10']:.1f} of his; Cape St Vincent to Sera spans {R['stretch']['ptol_span']:.1f} degrees for a real {R['stretch']['true_span']:.1f}.
- Error (median great-circle distance): as written, aligned on Alexandria, {f['f0']['median_km']} km; longitude stretch and shift (3 parameters) {f['f1']['median_km']} km; affine (6) {f['f2']['median_km']} km; Helmert (4) {f['f3']['median_km']} km; stretch per regional map {f['f4']['median_km']} km.
- Distance from Alexandria: as written, median error {R['alex']['near_f0']} km within 1,000 km, {R['alex']['far_f0']} km beyond 4,000 km (rank correlation {R['alex']['spearman_f0']:.2f}).
- Scotland: turned {sc['turn']:.0f} degrees clockwise relative to England and Wales; Solway to Duncansby Head bears {sc['brg_true']} degrees in reality, {sc['brg_ptol']} on his map.
- India: Barygaza to Cape Komaria spans {ind['lat_span_ptol']} degrees of latitude on his map, {ind['lat_span_true']} in reality. Taprobane spans {tp['lat_span_o']} degrees (real {tp['lat_span']}) and about {tp['area_ratio']} times the real area.
- Caspian: real mouths spread {cs['ns_true']} km N-S by {cs['ew_true']} km E-W, his {cs['ns_ptol']} by {cs['ew_ptol']} km; Oxus and Jaxartes really end in the Aral Sea, {N(cs['oxus_to_caspian_km'])} and {N(cs['jaxartes_to_caspian_km'])} km from the Caspian. Kattigara is {R['ocean']['kattigara_south_deg']} degrees too far south.
- Regions (shape error after each map's own Helmert fit, maps with at least {R['min_n']} places): best Sardinia and Sicily {g['EU07']['shape_km']} km, Dacia, Moesia and Thrace {g['EU09']['shape_km']} km, Greece {g['EU10']['shape_km']} km; worst British Isles {g['EU01']['shape_km']} km, Inner Libya and Ethiopia {g['AF04']['shape_km']} km, India {g['AS10']['shape_km']} km.
- Recensions: of {N(rc['both'])} entries in both, {rc['same_pct']:.0f}% identical; median difference {rc['median_diff_arcmin']} arcminutes where they differ; both fit reality with a median {rc['fit_omega_km']} km.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/catalogue.csv` | Grasshoff and Defaux's catalogue (all {N(s['rows'])} rows, CC BY 4.0) with my added columns: chapter, region, regional map, feature type, starred flag, name variants. |
| `data/matches.csv` | Every matched entry: modern coordinates, method, confidence, gazetteer and id, consistency with neighbours. |
| `data/unmatched_points.csv` | Identified point entries not matched, with the reason. |
| `data/places.csv` | The analysis set: one row per real place, Ptolemy's Omega and Xi coordinates, real coordinates, errors under each transform. |
| `data/regions.csv` | Errors by regional map. |
| `data/fit.json`, `data/results.json`, `data/site.json` | Fitted transforms; every number used; page data. |
| `data/coasts.json` | Ptolemy's coastal sections, his points joined in his order. |
| `data/world.json`, `data/caspian.json` | Natural Earth outlines (simplified) and the Caspian shore. |
| `code/` | Scripts, run in order; `reading.py` (hand coordinates, exonyms, rejected matches); page, paper and blog templates; `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Points only, and only entries the editors identify. Feature type from the German name.
- Gazetteers: Pleiades {R['meta']['pleiades_version']} (places, names, place types), DARE (Latin, Greek and modern names), Natural Earth towns. A match must lie in a generous box around Ptolemy's chapter. Names compared on spelling skeletons (Greek and Latin orthography, German transliteration).
- Hand coordinates (`code/reading.py`) for capes, river mouths, estuaries and some eastern cities, following the editors' identification, to about 5 km.
- Consistency check: each match's residual under a per-map stretch fit is compared with the median of its 8 nearest neighbours on Ptolemy's map; one-name matches more than 300 km out of line dropped ({m['dropped_dev']}), others inspected ({m['rejected']} rejected).
- Transforms: F0 as written (aligned on Alexandria), F1 lon = a + b x lon, lat = lat + c, F2 affine, F3 Helmert on grids with the aspect of 36 degrees, F4 F1 per regional map; shape = Helmert per regional map in local km. Errors are great-circle distances.
- Caveats: the identified places favour the Roman Mediterranean (only {m['india_east']} east of 60 degrees east); identifications are the editors' scholarship; coasts and deltas have moved; Ptolemy's coasts here are his points joined in order, not his drawing.

## How to rerun

Needs Python 3 with numpy, pandas, scipy, shapely, pyproj, matplotlib, Pillow, openpyxl and fontTools, xelatex and pdftotext; node with Playwright for `code/qa.js`. Steps 01 and 02 read `raw/PtolemyCatalogue.xlsx` (not published) and local copies of Pleiades, DARE and Natural Earth (paths in `code/common.py`); from step 03 on only `data/` is needed. Intermediate files go to `/dev/shm/ptolemy/work` (set `PTTMP` to change).

```
python3 code/01_parse.py        # catalogue, feature types, name variants
python3 code/02_geo.py          # outlines, gazetteer and hand matching, consistency check
python3 code/03_fit.py          # transforms, residuals, Ptolemy's coasts
python3 code/04_results.py      # results.json, regions.csv, site.json
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 reddit/collage.py       # collage
python3 code/08_readme.py       # README, LICENSE, Reddit post
python3 code/09_release.py      # blog post, Zenodo files
```

## Sources and licences

- Grasshoff, G. and Defaux, O. (2019) Catalog of Ptolemy's Geography, main books. Zenodo. https://doi.org/{CAT_DOI}. CC BY 4.0.
- Pleiades: a gazetteer of past places, version {R['meta']['pleiades_version']}, https://pleiades.stoa.org/. CC BY 3.0.
- Digital Atlas of the Roman Empire (DARE), J. Ahlfeldt, https://dare.ht.lu.se/, as packaged in the Klokan Technologies Roman Empire vector map. CC BY-SA.
- Natural Earth (public domain). Optional relief tiles on the page: Esri.

## Citation

Hotham, T. (2026) Ptolemy's world, measured: the coordinates of the Geography set against a modern map. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

lic = open("/home/claude/studies/rocket-launches/LICENSE", encoding="utf-8").read().split("\n\n\nThis licence covers")[0]
lic += """


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post, the figures and the derived data
files in data/ are released under CC BY 4.0. data/catalogue.csv and the
Ptolemaic coordinates throughout are derived from Grasshoff and Defaux (2019),
Catalog of Ptolemy's Geography, doi:10.5281/zenodo.3585758, CC BY 4.0: please
credit them. Positions matched from the Pleiades gazetteer are derived from
Pleiades (pleiades.stoa.org), CC BY 3.0: please credit Pleiades. Positions
matched from the Digital Atlas of the Roman Empire (DARE) are CC BY-SA.
Natural Earth is public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)

post = f"""## Title

[OC] I put Ptolemy's 1,900-year-old coordinates of the known world on a real map. Shrink his longitudes by {f['b']:.2f} and it snaps into place, but Scotland still points east and Sri Lanka is {tp['area_ratio']:.0f}x too big

## Body

Around AD 150 Ptolemy wrote down the known world as a table: a longitude and latitude for every town, cape and river mouth from Ireland to China. Using an open edition of that table ({N(s['with_coords'])} places with coordinates), I matched {N(m['places'])} of his places to where they really are, through ancient-place gazetteers and my own work on capes and river mouths. Read as written, the median place is {f['f0']['median_km']} km out, and the further from Alexandria, the worse it gets. Almost all of that is one error: his world is too wide. Shrink his longitudes by {f['b']:.2f} (close to 500/700, the ratio his too-small Earth implies) and the median error drops to {f['f1']['median_km']} km. What is left is local: Scotland turned {sc['turn']:.0f} degrees east, India flattened, Sri Lanka swollen across the equator, a round Caspian. Caveats: the identified places favour the Roman Mediterranean; the identifications are scholars', and some (like China) are debated. Interactive side-by-side map: {PAGE}

## Source comment

Sources: Grasshoff and Defaux (2019) Catalog of Ptolemy's Geography (Zenodo, CC BY 4.0) for the coordinates and identifications; Pleiades gazetteer (CC BY 3.0); Digital Atlas of the Roman Empire (CC BY-SA); Natural Earth.

Tools: Python (pandas, numpy, scipy, shapely, matplotlib); MapLibre for the interactive maps.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
for t in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("readme, licence, post ok")
