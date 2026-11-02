## Title

[OC] I put Ptolemy's 1,900-year-old coordinates of the known world on a real map. Shrink his longitudes by 0.72 and it snaps into place, but Scotland still points east and Sri Lanka is 15x too big

## Body

Around AD 150 Ptolemy wrote down the known world as a table: a longitude and latitude for every town, cape and river mouth from Ireland to China. Using an open edition of that table (6,372 places with coordinates), I matched 2,358 of his places to where they really are, through ancient-place gazetteers and my own work on capes and river mouths. Read as written, the median place is 425 km out, and the further from Alexandria, the worse it gets. Almost all of that is one error: his world is too wide. Shrink his longitudes by 0.72 (close to 500/700, the ratio his too-small Earth implies) and the median error drops to 144 km. What is left is local: Scotland turned 78 degrees east, India flattened, Sri Lanka swollen across the equator, a round Caspian. Caveats: the identified places favour the Roman Mediterranean; the identifications are scholars', and some (like China) are debated. Interactive side-by-side map: https://maps.tristanhotham.com/ptolemy/

## Source comment

Sources: Grasshoff and Defaux (2019) Catalog of Ptolemy's Geography (Zenodo, CC BY 4.0) for the coordinates and identifications; Pleiades gazetteer (CC BY 3.0); Digital Atlas of the Roman Empire (CC BY-SA); Natural Earth.

Tools: Python (pandas, numpy, scipy, shapely, matplotlib); MapLibre for the interactive maps.

Interactive version: https://maps.tristanhotham.com/ptolemy/
Paper: https://doi.org/10.5281/zenodo.23882603
Blog post: https://blog.tristanhotham.com/2026/10/31/ptolemy/
