"""Read the NASA Meteorite Landings table, check it against two other mirrors, clean it, and give every meteorite a
broad class group, a recovery region (Antarctica, Sahara, Arabia, other hot deserts, rest of the world) and a
present-day country.

Cleaning:
  * year: the table stores dates as "01/01/YYYY 12:00:00 AM"; only the year is meaningful. One year in the future
    (Northwest Africa 7701, given as 2101) is set to missing.
  * coordinates: missing, or exactly (0, 0), means the find site is not known (many desert meteorites are bought
    from dealers and are named only for a broad area such as "Northwest Africa").
  * Meridiani Planum is a meteorite found on Mars by the Opportunity rover; it is kept in the data with a flag but left
    out of every count about the Earth.
Region: from the point if there is one (Antarctica = south of 60 S; desert boxes below), otherwise from the
collection area in the name (the part before the number), if at least 80% of that area's located meteorites share one
region. Desert boxes are rough rectangles, documented here and in the paper."""
import numpy as np, pandas as pd
from collections import Counter
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

A = pd.read_csv(f"{RAW}/a/Meteorite_Landings.csv", dtype=str, keep_default_na=False)
C = pd.read_csv(f"{RAW}/c/Meteorite_Landings.csv", dtype=str, keep_default_na=False)
B = pd.read_csv(f"{RAW}/b/meteorite_landings.csv", dtype=str, keep_default_na=False)

# ---------- check the copies against each other ----------
chk = {"rows_a": len(A), "rows_c": len(C), "rows_b": len(B)}
A = A.sort_values("id", key=lambda s: s.astype(int)).reset_index(drop=True)
C = C.sort_values("id", key=lambda s: s.astype(int)).reset_index(drop=True)
assert len(A) == len(C) and (A["id"] == C["id"]).all()
num = lambda s: pd.to_numeric(s.replace("", np.nan), errors="coerce")
diff = {}
for col in ("name", "nametype", "recclass", "fall", "year"):
    diff[col] = int((A[col] != C[col]).sum())
for col in ("mass (g)", "reclat", "reclong"):
    x, y = num(A[col]), num(C[col])
    diff[col] = int(((x - y).abs().gt(1e-6) | (x.isna() != y.isna())).sum())
chk["a_vs_c_cells_differing"] = diff
# the only differences: three finds with no year in copy a whose year in copy c is garbled (0301, 2501, 0601,
# archaeological finds the source dates loosely); I keep them without a year
yd = A["year"] != C["year"]
chk["year_only_in_c"] = A.loc[yd, "name"].tolist()
assert (A.loc[yd, "year"] == "").all() and yd.sum() == 3
assert sum(v for k, v in diff.items() if k != "year") == 0, diff
# third copy: five columns, its own row order
bb = B.set_index("name")
m = A.set_index("name").join(bb, rsuffix="_b", how="inner")
chk["b_names_matched"] = len(m)
chk["b_mass_differ"] = int(((num(m["mass (g)"]) - num(m["mass"])).abs().gt(1e-6) | (num(m["mass (g)"]).isna() != num(m["mass"]).isna())).sum())
chk["b_lat_differ"] = int(((num(m["reclat"]) - num(m["reclat_b"])).abs().gt(1e-6)).sum())
chk["b_year_differ"] = int((m["year"].str[6:10] != m["year_b"].str[:4]).sum())
print("copies:", chk)

# ---------- clean ----------
D = pd.DataFrame({"id": A["id"].astype(int), "name": A["name"], "nametype": A["nametype"], "recclass": A["recclass"],
                  "fall": A["fall"].map({"Fell": "Fell", "Found": "Found"}),
                  "mass_g": num(A["mass (g)"]), "year": num(A["year"].str[6:10]),
                  "lat": num(A["reclat"]), "lon": num(A["reclong"])})
assert D["fall"].notna().all()
D["flag"] = ""
fut = D["year"] > 2026
D.loc[fut, "flag"] = "year in the future in the source, set to missing"
chk["future_years"] = D.loc[fut, "name"].tolist()
D.loc[fut, "year"] = np.nan
mars = D["name"].eq("Meridiani Planum")
D.loc[mars, "flag"] = "found on Mars by the Opportunity rover; left out of Earth counts"
nopt = D["lat"].isna() | D["lon"].isna() | ((D["lat"] == 0) & (D["lon"] == 0)) | mars
chk["coords_missing"] = int((D["lat"].isna()).sum())
chk["coords_zero"] = int(((D["lat"] == 0) & (D["lon"] == 0)).sum())
D.loc[nopt, ["lat", "lon"]] = np.nan
D["area"] = D["name"].str.replace(r"\s+[A-Za-z]{0,3}\d[\w\-,./]*.*$", "", regex=True).str.strip()

# ---------- class groups ----------
ACH = ("Enst achon", "Eucrite", "Diogenite", "Howardite", "Ureilite", "Aubrite", "Angrite", "Acapulcoite", "Lodranite", "Winonaite",
       "Brachinite", "Achondrite")


def group(c):
    if c.startswith("Martian"): return "Martian"
    if c.startswith("Lunar"): return "Lunar"
    if c.startswith("Iron"): return "Iron"
    if c.startswith(("Pallasite", "Mesosiderite")): return "Stony-iron"
    if c.startswith(ACH): return "Achondrite"
    if re.match(r"^(LL|L|H)(?![a-z])", c) or c.startswith("OC"): return "Ordinary chondrite"
    if re.match(r"^C(?![a-z])", c): return "Carbonaceous chondrite"
    if re.match(r"^(E|EH|EL|R|K)(?![a-z])", c) or c.startswith("Chondrite"): return "Other chondrite"
    return "Relict or unclassified"


D["group"] = D["recclass"].map(group)
gc = Counter(D["group"])
print("groups", dict(gc))
print("unclassified classes", Counter(D.loc[D.group == "Unclassified", "recclass"]).most_common(12))

# ---------- regions ----------
BOX = {"Sahara": (-17.5, 15, 34, 34),            # lon0, lat0, lon1, lat1
       "Arabia": (35, 12, 60, 31),
       "Atacama": (-71.5, -30, -68, -18),
       "Australian deserts": (117, -32.5, 141, -19)}
HOT_OTHER = ("Atacama", "Australian deserts")


def region_of(lon, lat):
    if np.isnan(lat): return None, None
    if lat < -60: return "Antarctica", None
    for k, (x0, y0, x1, y1) in BOX.items():
        if x0 <= lon <= x1 and y0 <= lat <= y1:
            return ("Other hot deserts", k) if k in HOT_OTHER else (k, None)
    return "Rest of the world", None


rr = [region_of(x, y) for x, y in zip(D["lon"], D["lat"])]
D["region"] = [r[0] for r in rr]; D["desert"] = [r[1] or "" for r in rr]
D["region_from"] = np.where(D["region"].notna(), "point", "")
loc = D[D["region"].notna()]
area_reg = {}
for a, g in loc.groupby("area"):
    c = Counter(g["region"]); k, n = c.most_common(1)[0]
    if len(g) >= 3 and n / len(g) >= .8:
        area_reg[a] = k
inf = D["region"].isna() & D["area"].map(lambda a: a in area_reg) & ~mars
D.loc[inf, "region"] = D.loc[inf, "area"].map(area_reg); D.loc[inf, "region_from"] = "name"
D.loc[D["region"].isna(), "region"] = "Not known"
D.loc[mars, "region"] = "Mars"
chk["region_from_name"] = int(inf.sum())
print("regions", Counter(D["region"]), "inferred from name", int(inf.sum()))

# ---------- countries (present-day, Natural Earth 1:10m) ----------
W10 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]
geoms = [(iso_of(f["properties"]), shape(f["geometry"]).buffer(0)) for f in W10["features"]]
tree = STRtree([g for _, g in geoms])


def at(lon, lat):
    pt = Point(lon, lat)
    hit = [geoms[i][0] for i in tree.query(pt) if geoms[i][1].covers(pt)]
    if hit: return hit[0]
    near = [(geoms[i][1].distance(pt), geoms[i][0]) for i in tree.query(pt.buffer(.3))]
    near = [x for x in near if x[0] < .3]
    return min(near)[1] if near else None


D["iso"] = [at(x, y) if not np.isnan(y) else None for x, y in zip(D["lon"], D["lat"])]
D["iso"] = D["iso"].replace({"CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "PSX": "PSE", "SAH": "ESH", "KAS": "IND", "SOL": "SOM"})
chk["located_no_country"] = int((D["lat"].notna() & D["iso"].isna()).sum())
print("located without a country", chk["located_no_country"], D.loc[D["lat"].notna() & D["iso"].isna(), "name"].head(8).tolist())

D.to_pickle(f"{WORK}/met.pkl")
jsave(chk, f"{WORK}/checks.json")
jsave({"boxes": BOX, "area_region": area_reg}, f"{WORK}/regions.json")
print("rows", len(D), "located", int(D["lat"].notna().sum()), "falls", int((D.fall == "Fell").sum()))
