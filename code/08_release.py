"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23847548, https://doi.org/10.5281/zenodo.23847548 and https://blog.tristanhotham.com/2026/10/31/meteorite-falls/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Where_Space_Rocks_Land"

# the page build checks the shared facts; these are numbers written in words or alt text in the blog
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "04_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
CO = R["continents"]
assert [(CO[k]["falls"], round(CO[k]["expected"])) for k in ("Europe", "Asia", "North America", "Africa", "South America", "Oceania", "Antarctica")] == \
       [(374, 171), (325, 232), (183, 181), (141, 223), (52, 131), (19, 63), (0, 92)]
assert R["finds_time"]["peak_n"] > 17000 and R["falls_time"]["peak_n"] == 91 and R["falls_time"]["d1800"] < 20
assert round(R["classes"]["Iron"]["rest_pct"]) == 27 and R["countries"]["JPN"]["expected"] < 3
assert all(R["countries"][k]["ratio"] > 10 for k in ("ITA", "FRA", "DEU"))
assert 1.8 < 1 + R["falls_time"]["pop_growth_pct"] / 100 < 2.2          # "roughly doubled"
assert R["heaviest"][0]["y"] == 1920

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG|DOI_URL|BLOG_URL|DOI\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
s = R["source"]
meta = {"title": "Where space rocks land, and why the meteorite record is so lumpy",
        "slug": "meteorite-falls",
        "excerpt": f"I mapped {s['n']:,} meteorites from the Meteoritical Society's catalogue. {R['regions']['Antarctica']['pct']:.0f}% were found on Antarctic ice and {R['hot']['pct']:.0f}% in hot deserts, while the {s['falls']:,} seen to fall follow people, not the sky.",
        "seo_description": f"A map of {s['n']:,} meteorites: why most were found on Antarctic ice and in deserts, and why witnessed falls cluster where people live.",
        "tags": ["meteorites", "maps", "data visualisation", "Antarctica", "Sahara", "space", "NASA open data"],
        "header_alt": f"Title card reading 'Where space rocks land' in black, orange and blue on pale paper, beside a world map with orange dots for witnessed falls across Europe, India, Japan and the United States, ochre and purple desert finds in the Sahara and Oman, and blue circles on Antarctica. Text: {s['n']:,} meteorites; {R['regions']['Antarctica']['pct']:.0f}% found on Antarctic ice and {R['hot']['pct']:.0f}% in hot deserts; the {s['falls']:,} seen to fall follow people."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/meteorite-falls_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"meteorite-falls/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"meteorite-falls/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "meteorite-falls/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
zmeta = {"title": "Where Space Rocks Land: Falls, Finds and the Geography of the Meteorite Record",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p><p>Meteorite data: The Meteoritical Society, Meteoritical Bulletin Database, as published by NASA's Open Data Portal.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["meteorites", "meteorite falls", "Antarctic meteorites", "hot desert meteorites", "sampling bias", "Meteoritical Bulletin", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.lpi.usra.edu/meteor/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://data.nasa.gov/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
