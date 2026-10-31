"""Shared paths and helpers for the meteorite-falls project.

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw/meteorites/a/Meteorite_Landings.csv
      NASA Open Data Portal "Meteorite Landings" (data.nasa.gov, dataset gh4g-9sfh), compiled from the Meteoritical
      Society's Meteoritical Bulletin Database. Copy taken from the GitHub mirror
      https://raw.githubusercontent.com/stefmolin/pandas-workshop/main/data/Meteorite_Landings.csv (retrieved 2026).
  /home/claude/newdata/raw/meteorites/c/Meteorite_Landings.csv
      Second, independent mirror of the same file, used as a check:
      https://raw.githubusercontent.com/hi-primus/optimus/develop/examples/data/Meteorite_Landings.csv
  /home/claude/newdata/raw/meteorites/b/meteorite_landings.csv
      Third mirror (OpenLayers examples, five columns only: name, mass, year, lat, lon), used as a further check.
  /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson, ne_50m_admin_0_countries.geojson,
      ne_10m_populated_places_simple.geojson (Natural Earth, public domain; POP_EST used as a rough population)
  /home/claude/newdata/raw/wb/population.csv (World Bank world population 1960 onwards, CC BY 4.0)
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("MET_RAW", "/home/claude/newdata/raw/meteorites")
GEO = os.environ.get("MET_GEO", "/home/claude/newdata/raw/geo")
WB = os.environ.get("MET_WB", "/home/claude/newdata/raw/wb/population.csv")
FONTS = os.environ.get("MET_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("METTMP", "/dev/shm/meteorites"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "meteorite-falls"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23847548"            # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/meteorite-falls/"      # filled in by the publisher
RETRIEVED = "2026"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
METBULL = "https://www.lpi.usra.edu/meteor/metbull.php?code="

# broad meteorite groups (order = legend order) and their colours
GROUPS = [("Ordinary chondrite", "#C9772B"), ("Carbonaceous chondrite", "#3B3B3B"), ("Other chondrite", "#B59A3A"),
          ("Achondrite", "#3E7CB1"), ("Lunar", "#8E8E99"), ("Martian", "#B23A2E"),
          ("Stony-iron", "#5E8C4A"), ("Iron", "#5B4A8B"), ("Relict or unclassified", "#A9A398")]
# where a meteorite was recovered (order = legend order)
REGIONS = [("Antarctica", "#2F7FB8"), ("Sahara", "#D98A1F"), ("Arabia", "#8E5BA8"), ("Other hot deserts", "#B58B52"),
           ("Rest of the world", "#5E6B63"), ("Not known", "#B9B3A6")]


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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
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
    if f == "t": return f"{float(v) / 1e6:.1f}"          # grams to tonnes
    raise ValueError(f)
