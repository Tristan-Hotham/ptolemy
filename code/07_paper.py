"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them). The DOI stays as the 10.5281/zenodo.23882603 placeholder."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Ptolemy"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# statements made in words in the paper only
assert R["fit"]["f0_to_f1_drop_pct"] >= 64                                   # "two thirds of the error"
assert R["alex"]["spearman_f1"] < R["alex"]["spearman_f0"]
assert R["regions"]["EU10"]["shape_km"] < 100 and R["regions"]["EU06"]["shape_km"] < 100   # "well under 100 km"


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "pc1": return f"{float(v):.1f}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


F = R["fit"]
rows = [("F0 as written (aligned on Alexandria)", 0, F["f0"]), ("F1 longitude stretch and shift", 3, F["f1"]), ("F2 affine", 6, F["f2"]),
        ("F3 Helmert (rotation, scale, shift)", 4, F["f3"]), ("F4 F1 per regional map", "3 per map", F["f4"])]
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{Error of each transform from Ptolemy's coordinates to modern ones (km).}\\label{tab:fits}"
      "\\begin{tabular}{lrrrr}\\toprule Transform & Parameters & Median & RMS & 90th pct.\\\\\\midrule\n" +
      "".join(f"{a} & {b} & {c['median_km']:,} & {c['rms_km']:,} & {c['p90_km']:,}\\\\\n" for a, b, c in rows) + "\\bottomrule\\end{tabular}\\end{table}")
G = pd.read_csv(f"{DATA}/regions.csv")
fm = lambda v: "" if pd.isna(v) else f"{int(v):,}"
rows = "".join(f"{tex(r.name)} & {r.n} & {fm(r.shape_km) if r.ranked else '(' + fm(r.shape_km) + ')' if pd.notna(r.shape_km) else ''} & {fm(r.f1_km)} & {fm(r.f0_km)} & {r.lat_err:+.1f}\\\\\n" for r in G.itertuples())
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Ptolemy's 26 regional maps: matched places, median shape error, median error under F1 and as written (km), and median latitude error (degrees, positive too far north). Shape errors in brackets rest on fewer than " + str(R["min_n"]) + " places.}\\label{tab:regions}"
      "\\begin{tabular}{lrrrrr}\\toprule Regional map & Places & Shape & F1 & F0 & Latitude\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|meta\.doi)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("FITS", TF), ("REGIONS", TR)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = t.replace("\\href{https://doi.org/{{meta.doi}}}{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
assert "{{" not in t and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
