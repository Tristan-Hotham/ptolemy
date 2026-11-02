"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, world.json) is embedded. Facts stated in words are checked here.
The full-screen map snippet (code/fullscreen_snippet.html) is pasted before </body>. 10.5281/zenodo.23882603 and https://blog.tristanhotham.com/2026/10/31/ptolemy/ stay
as placeholders for the publisher."""
import json
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
KEEP = {"DOI", "BLOG_URL", "DOI_URL"}
G, F = R["regions"], R["fit"]

# facts stated in words (page, blog, paper, collage)
assert abs(F["b"] - F["stadia_ratio"]) / F["stadia_ratio"] < .02                      # "within x% of 500/700"
assert F["f1"]["median_km"] <= F["f2"]["median_km"] + 5 and F["f1"]["median_km"] <= F["f3"]["median_km"] + 5   # "does as well as"
assert F["f4"]["median_km"] < F["f1"]["median_km"]
assert R["stretch"]["slope_alex"] > 1.3 and R["stretch"]["ratio"] > 1.4
assert R["alex_bins"][0]["f0_km"] < R["alex_bins"][1]["f0_km"] < R["alex_bins"][2]["f0_km"] < R["alex_bins"][3]["f0_km"]
assert R["places"]["Samarkand"]["f1_km"] < 100 and R["places"]["Rome"]["f1_km"] < 100
assert R["lat"]["britain"] > 2 and R["lat"]["africa"] < -3                              # Britain north, Africa south
assert R["scotland"]["brg_true"] < 15 and 70 < R["scotland"]["brg_ptol"] < 100        # "almost due north", "almost due east"
assert R["scotland"]["turn"] > 60
assert 150 < R["india"]["brg_true"] < 170 and 100 < R["india"]["brg_ptol"] < 125      # SSE vs ESE
assert R["taprobane"]["equator_crossed"] and R["taprobane"]["area_ratio"] > 10
assert R["caspian"]["ns_true"] > 2 * R["caspian"]["ew_true"] and abs(R["caspian"]["ratio_ptol"] - 1) < .25   # "as wide as it is long"
assert R["rank_shape"][:3] == ["EU07", "EU09", "EU10"] and R["rank_shape"][-3:] == ["EU01", "AF04", "AS10"]
assert R["rank_f1"][:2] == ["AS04", "AF03"]
assert R["rec"]["fit_omega_km"] == R["rec"]["fit_xi_km"] and R["rec"]["xi_closer"] > R["rec"]["omega_closer"]
assert max(R["rec"]["by_book"], key=lambda k: R["rec"]["by_book"][k]["pct"]) == "2" and min(R["rec"]["by_book"], key=lambda k: R["rec"]["by_book"][k]["pct"]) == "5"
assert 11 < R["fit"]["prime_meridian_w"] < 14.5                                        # "about where the eastern Canaries are"
assert R["match"]["india_east"] < 100


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{(?!DOI\}\}|BLOG_URL\}\}|DOI_URL\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    left = set(re.findall(r"\{\{([^}]*)\}\}", html))
    assert left <= KEEP, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
