# Ptolemy's world, measured

The coordinates of Ptolemy's Geography (about AD 150) set against a modern map: 2,358 of his places matched to where they really are, the stretch in his longitudes, how the error grows with distance from Alexandria, Scotland turned east, India flattened and Taprobane swollen, the Caspian and the Indian Ocean as closed seas, the best and worst of his 26 regional maps, and how far the Omega and Xi recensions differ.

Interactive page: https://maps.tristanhotham.com/ptolemy/
Paper: https://doi.org/10.5281/zenodo.23882603
Blog post: https://blog.tristanhotham.com/2026/10/31/ptolemy/

## Headline results

- Source: 10,049 catalogue entries, 6,372 with coordinates (6,338 Omega, 4,440 Xi). Of 5,667 point features (towns, capes, river mouths, harbours, islands) with coordinates, the editors identify 2,871 (51%).
- Matching: 2,439 identified points matched (85%), 2,358 distinct places: 1436 where a gazetteer's ancient and modern names both agree (high), 261 by ancient name and 202 by modern name alone (medium), 459 by hand (capes, river mouths, eastern cities). 74% high confidence. Europe 1365, Africa 297, Asia 696.
- The stretch: real longitude = -12.94 + 0.7189 x Ptolemy's. 500/700 = 0.714, the ratio implied by his 500-stadia degree. Every 10 degrees of real longitude from Alexandria is 13.7 of his; Cape St Vincent to Sera spans 174.8 degrees for a real 117.9.
- Error (median great-circle distance): as written, aligned on Alexandria, 425 km; longitude stretch and shift (3 parameters) 144 km; affine (6) 142 km; Helmert (4) 144 km; stretch per regional map 105 km.
- Distance from Alexandria: as written, median error 134 km within 1,000 km, 1445 km beyond 4,000 km (rank correlation 0.91).
- Scotland: turned 78 degrees clockwise relative to England and Wales; Solway to Duncansby Head bears 3 degrees in reality, 79 on his map.
- India: Barygaza to Cape Komaria spans 3.8 degrees of latitude on his map, 13.6 in reality. Taprobane spans 15.0 degrees (real 3.9) and about 14.6 times the real area.
- Caspian: real mouths spread 1054 km N-S by 387 km E-W, his 815 by 790 km; Oxus and Jaxartes really end in the Aral Sea, 470 and 620 km from the Caspian. Kattigara is 29.5 degrees too far south.
- Regions (shape error after each map's own Helmert fit, maps with at least 15 places): best Sardinia and Sicily 42 km, Dacia, Moesia and Thrace 52 km, Greece 52 km; worst British Isles 128 km, Inner Libya and Ethiopia 448 km, India 528 km.
- Recensions: of 4,406 entries in both, 69% identical; median difference 20 arcminutes where they differ; both fit reality with a median 144 km.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/catalogue.csv` | Grasshoff and Defaux's catalogue (all 10,049 rows, CC BY 4.0) with my added columns: chapter, region, regional map, feature type, starred flag, name variants. |
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
- Gazetteers: Pleiades 4.1 (places, names, place types), DARE (Latin, Greek and modern names), Natural Earth towns. A match must lie in a generous box around Ptolemy's chapter. Names compared on spelling skeletons (Greek and Latin orthography, German transliteration).
- Hand coordinates (`code/reading.py`) for capes, river mouths, estuaries and some eastern cities, following the editors' identification, to about 5 km.
- Consistency check: each match's residual under a per-map stretch fit is compared with the median of its 8 nearest neighbours on Ptolemy's map; one-name matches more than 300 km out of line dropped (21), others inspected (2 rejected).
- Transforms: F0 as written (aligned on Alexandria), F1 lon = a + b x lon, lat = lat + c, F2 affine, F3 Helmert on grids with the aspect of 36 degrees, F4 F1 per regional map; shape = Helmert per regional map in local km. Errors are great-circle distances.
- Caveats: the identified places favour the Roman Mediterranean (only 67 east of 60 degrees east); identifications are the editors' scholarship; coasts and deltas have moved; Ptolemy's coasts here are his points joined in order, not his drawing.

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

- Grasshoff, G. and Defaux, O. (2019) Catalog of Ptolemy's Geography, main books. Zenodo. https://doi.org/10.5281/zenodo.3585758. CC BY 4.0.
- Pleiades: a gazetteer of past places, version 4.1, https://pleiades.stoa.org/. CC BY 3.0.
- Digital Atlas of the Roman Empire (DARE), J. Ahlfeldt, https://dare.ht.lu.se/, as packaged in the Klokan Technologies Roman Empire vector map. CC BY-SA.
- Natural Earth (public domain). Optional relief tiles on the page: Esri.

## Citation

Hotham, T. (2026) Ptolemy's world, measured: the coordinates of the Geography set against a modern map. Zenodo. https://doi.org/10.5281/zenodo.23882603

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
