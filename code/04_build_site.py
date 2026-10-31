"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, world.json, cities) is embedded; data/points.json is loaded by the page.
Facts stated in words are checked here. The full-screen map snippet (code/fullscreen_snippet.html) is pasted before </body>."""
import json
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
C, RG, K = R["countries"], R["regions"], R["classes"]

# facts stated in words (page, blog, paper, collage)
assert RG["Antarctica"]["falls"] == 0 and RG["Antarctica"]["n"] > RG["Sahara"]["n"] > RG["Arabia"]["n"]
assert R["source"]["checks"]["a_vs_c_cells_differing"]["year"] == 3 and len(R["source"]["checks"]["year_only_in_c"]) == 3
assert [r["iso"] for r in C["ratio_top"][:5]] == ["JPN", "ITA", "FRA", "DEU", "GBR"] and all(r["ratio"] > 10 for r in C["ratio_top"][:5])
assert C["DEU"]["ratio"] < C["FRA"]["ratio"] < C["ITA"]["ratio"]
assert C["LBY"]["falls"] == 1 and C["LBY"]["finds"] > 1000
assert C["CAN"]["ratio"] < .3 and C["BRA"]["ratio"] < .5 and C["AUS"]["ratio"] < .5
assert C["USA"]["falls"] > C["IND"]["falls"] > C["FRA"]["falls"] and C["top"][0]["iso"] == "USA"
CO = R["continents"]
assert CO["Europe"]["ratio"] > CO["Asia"]["ratio"] > CO["North America"]["ratio"] > 1 > CO["Africa"]["ratio"] > CO["South America"]["ratio"] > CO["Oceania"]["ratio"]
assert abs(CO["North America"]["ratio"] - 1) < .05
assert R["falls_time"]["peak_dec"] == 1930 and R["falls_time"]["oldest"][0]["name"] == "Nogata" and R["falls_time"]["oldest"][1]["name"] == "Narni"
assert abs(R["falls_time"]["falls_change_pct"]) < 10 and R["falls_time"]["pop_growth_pct"] > 90
assert R["antarctic"]["yamato"]["y"] == 1969 and R["antarctic"]["first"]["name"] == "Adelie Land"
assert R["finds_time"]["peak_dec"] == 2000
assert R["mass"]["top10_iron"] == 10 and R["heaviest_falls"][0]["name"] == "Sikhote-Alin" and [h["name"] for h in R["heaviest_falls"][1:3]] == ["Jilin", "Allende"]
assert R["heaviest"][0]["country"] == "Namibia" and R["heaviest"][1]["country"] == "Greenland" and R["heaviest"][2]["country"] == "Argentina"
assert K["Iron"]["rest_pct"] > 5 * K["Iron"]["falls_pct"] and K["Ordinary chondrite"]["ant_pct"] > K["Ordinary chondrite"]["falls_pct"]
assert R["areas"][0]["area"] == "Yamato" and R["areas"][1]["area"] == "Northwest Africa"
assert R["countries"]["OMN"]["finds"] > 0.6 * RG["Arabia"]["n"]   # "Arabia, mostly Oman"
assert R["mass"]["median_ant"] < 20 and R["mass"]["median_rest_find"] > 1000


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{(?!DOI\}\}|BLOG_URL\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    assert "{{" not in html.replace("10.5281/zenodo.23847548", "").replace("https://blog.tristanhotham.com/2026/10/31/meteorite-falls/", ""), re.findall(r"\{\{[^}]*\}\}", html)[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
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
