"""Every number used anywhere (data/results.json), the reusable data tables (data/*.csv) and the page data
(data/points.json, data/site.json).

Expected falls under an even spread: meteorites arrive at a rate that is close to uniform over the Earth's surface (small
latitude effects are ignored), so if every fall were seen and reported, each country's share of witnessed falls on
land would equal its share of the land area (Antarctica included). Observed / expected > 1 means more falls were
recorded than an even spread predicts."""
import numpy as np, pandas as pd
from collections import Counter
from scipy.stats import spearmanr, pearsonr
from common import *

D0 = pd.read_pickle(f"{WORK}/met.pkl")
CHK = jload(f"{WORK}/checks.json"); REG = jload(f"{WORK}/regions.json")
M = jload(f"{WORK}/countries.json")
D0["iso"] = D0["iso"].where(D0["iso"].notna(), "").astype(str)
D = D0[D0["region"] != "Mars"].copy()
FALL = D[D["fall"] == "Fell"]; FIND = D[D["fall"] == "Found"]
pc = lambda a, b: round(100 * a / b, 2)
R = {}

# ---------- source ----------
loc = D["lat"].notna()
R["source"] = {"n_rows": len(D0), "n": len(D), "n_valid": int((D.nametype == "Valid").sum()), "n_relict": int((D.nametype == "Relict").sum()),
               "falls": len(FALL), "finds": len(FIND), "falls_pct": pc(len(FALL), len(D)), "finds_pct": pc(len(FIND), len(D)),
               "located": int(loc.sum()), "located_pct": pc(loc.sum(), len(D)), "unlocated": int((~loc).sum()),
               "falls_located": int(FALL["lat"].notna().sum()), "finds_located": int(FIND["lat"].notna().sum()),
               "coords_missing": CHK["coords_missing"], "coords_zero": CHK["coords_zero"],
               "nwa": int((D.area == "Northwest Africa").sum()), "nwa_unlocated": int(((D.area == "Northwest Africa") & ~loc).sum()),
               "region_from_name": CHK["region_from_name"], "no_year": int(D.year.isna().sum()), "with_mass": int(D.mass_g.notna().sum()),
               "last_year": int(D.year.max()), "n_last_year": int((D.year == D.year.max()).sum()),
               "n_classes": int(D.recclass.nunique()), "checks": CHK}
assert R["source"]["last_year"] == 2013

# ---------- regions ----------
REGN = [r for r, _ in REGIONS]
reg = {}
for r in REGN:
    a = D[D.region == r]
    reg[r] = {"n": len(a), "pct": pc(len(a), len(D)), "falls": int((a.fall == "Fell").sum()), "finds": int((a.fall == "Found").sum()),
              "falls_pct": pc((a.fall == "Fell").sum(), len(FALL)), "finds_pct": pc((a.fall == "Found").sum(), len(FIND)),
              "median_mass": float(a.loc[a.fall == "Found", "mass_g"].median()) if (a.fall == "Found").any() else None,
              "from_name": int((a.region_from == "name").sum())}
R["regions"] = reg
hot = ["Sahara", "Arabia", "Other hot deserts"]
R["hot"] = {"n": sum(reg[r]["n"] for r in hot), "pct": round(sum(reg[r]["pct"] for r in hot), 2),
            "sa_pct": round(reg["Sahara"]["pct"] + reg["Arabia"]["pct"], 2),
            "falls": sum(reg[r]["falls"] for r in hot),
            "by_desert": {k: int((D.desert == k).sum()) for k in ("Atacama", "Australian deserts")}}
R["icedesert"] = {"pct": round(reg["Antarctica"]["pct"] + R["hot"]["pct"], 2),
                  "finds_pct": round(reg["Antarctica"]["finds_pct"] + sum(reg[r]["finds_pct"] for r in hot), 2)}
R["rest"] = {"falls_pct": reg["Rest of the world"]["falls_pct"], "pct": reg["Rest of the world"]["pct"],
             "finds": reg["Rest of the world"]["finds"]}
assert reg["Antarctica"]["falls"] == 0
# collection areas
ar = D.groupby("area").agg(n=("id", "size"), region=("region", lambda s: s.mode().iloc[0]), first=("year", "min")).sort_values("n", ascending=False)
R["areas"] = [{"area": a, "n": int(r.n), "region": r.region, "first": None if np.isnan(r["first"]) else int(r["first"])} for a, r in ar.head(20).iterrows()]
R["areas_top_share"] = pc(ar.head(10).n.sum(), len(D))
# Antarctic history
ant = D[D.region == "Antarctica"].sort_values("year")
R["antarctic"] = {"first": {"name": ant.iloc[0]["name"], "y": int(ant.iloc[0].year)},
                  "yamato": {"y": int(D[D.area == "Yamato"].year.min()), "n_first": int(((D.area == "Yamato") & (D.year == 1969)).sum()), "n": int((D.area == "Yamato").sum())},
                  "pre1969": int((ant.year < 1969).sum()), "median_mass": reg["Antarctica"]["median_mass"]}
# finds by decade and region (1900s onwards), and falls by decade
DEC = list(range(1800, 2020, 10))
dec_rows = []
for d in DEC:
    row = {"dec": d, "falls": int(((FALL.year >= d) & (FALL.year < d + 10)).sum())}
    for r in REGN:
        row[r] = int(((FIND.year >= d) & (FIND.year < d + 10) & (FIND.region == r)).sum())
    row["finds"] = sum(row[r] for r in REGN)
    dec_rows.append(row)
R["decades"] = dec_rows
dd = {r["dec"]: r for r in dec_rows}
peak = max((r for r in dec_rows if r["dec"] < 2010), key=lambda r: r["falls"])
R["falls_time"] = {"peak_dec": peak["dec"], "peak_n": peak["falls"], "d1800": dd[1800]["falls"], "d1860": dd[1860]["falls"],
                   "pre1800": int((FALL.year < 1800).sum()), "since1950_mean": round(np.mean([dd[d]["falls"] for d in range(1950, 2010, 10)]), 1),
                   "d1960": dd[1960]["falls"], "d2000": dd[2000]["falls"], "d2010": dd[2010]["falls"],
                   "oldest": [{"name": r["name"], "y": int(r.year), "iso": r.iso, "country": M[r.iso]["name"]} for _, r in FALL.sort_values("year").head(6).iterrows()]}
wb = pd.read_csv(WB); w = wb[wb["Country Code"] == "WLD"].set_index("Year")["Value"]
p60, p00 = w.loc[1960:1969].mean(), w.loc[2000:2009].mean()
R["falls_time"]["pop_growth_pct"] = round(100 * (p00 / p60 - 1), 1)
R["falls_time"]["falls_change_pct"] = round(100 * (dd[2000]["falls"] / dd[1960]["falls"] - 1), 1)
R["finds_time"] = {"pre1970_pct": pc((FIND.year < 1970).sum(), FIND.year.notna().sum()), "since1970": int((FIND.year >= 1970).sum()),
                   "since1970_pct": pc((FIND.year >= 1970).sum(), FIND.year.notna().sum()),
                   "peak_dec": max(dec_rows, key=lambda r: r["finds"])["dec"], "peak_n": max(r["finds"] for r in dec_rows)}

# ---------- countries: falls against an even spread and against people ----------
fc = FALL["iso"].value_counts(); kc = FIND["iso"].value_counts()
land = sum(v["area"] for v in M.values())
nl = int((FALL["iso"] != "").sum())
rows = []
for iso, v in M.items():
    o = int(fc.get(iso, 0)); e = nl * v["area"] / land
    rows.append({"iso": iso, "name": v["name"], "continent": v["cont"], "falls": o, "finds": int(kc.get(iso, 0)),
                 "area_km2": round(v["area"]), "pop_est": int(v["pop"]), "expected": round(e, 2), "ratio": round(o / e, 2) if e > 0 else None,
                 "falls_per_m_km2": round(o / v["area"] * 1e6, 1) if v["area"] > 0 else None,
                 "falls_per_10m_people": round(o / v["pop"] * 1e7, 2) if v["pop"] > 0 else None,
                 "people_per_km2": round(v["pop"] / v["area"], 1) if v["area"] > 0 else None})
T = pd.DataFrame(rows).sort_values(["falls", "finds"], ascending=False)
T.to_csv(f"{DATA}/countries.csv", index=False)
Ti = T.set_index("iso")
big = T[T.area_km2 >= 20000]
s = spearmanr(big.falls / big.area_km2, big.pop_est / big.area_km2)
k = big[big.falls > 0]
p = pearsonr(np.log10(k.falls / k.area_km2), np.log10(k.pop_est / k.area_km2))
R["countries"] = {"n_with_falls": int((T.falls > 0).sum()), "n_big": len(big), "n_big_falls": len(k),
                  "spearman": round(float(s.statistic), 2), "pearson_log": round(float(p.statistic), 2),
                  "falls_land": nl, "land_m_km2": round(land / 1e6, 1),
                  "top": [{"iso": i, "name": r["name"], "falls": int(r.falls), "expected": float(r.expected), "ratio": float(r.ratio)} for i, r in Ti.head(15).iterrows()],
                  "ratio_top": [{"iso": i, "name": r["name"], "falls": int(r.falls), "ratio": float(r.ratio), "expected": float(r.expected)}
                                for i, r in Ti[Ti.expected >= 1.5].sort_values("ratio", ascending=False).head(12).iterrows()],
                  "ratio_low": [{"iso": i, "name": r["name"], "falls": int(r.falls), "ratio": float(r.ratio), "expected": float(r.expected)}
                                for i, r in Ti[Ti.expected >= 10].sort_values("ratio").head(10).iterrows()]}
for iso in ("USA", "IND", "FRA", "JPN", "DEU", "ITA", "GBR", "CHN", "RUS", "BRA", "AUS", "CAN", "ATA", "DZA", "LBY", "OMN", "MAR", "COD"):
    r = Ti.loc[iso]
    R["countries"][iso] = {"name": r["name"], "falls": int(r.falls), "finds": int(r.finds), "expected": float(r.expected), "ratio": float(r.ratio),
                           "per_10m": float(r.falls_per_10m_people or 0), "per_m_km2": float(r.falls_per_m_km2)}
# continents
cont = []
for c, g in T.groupby("continent"):
    o, e = int(g.falls.sum()), float(g.expected.sum())
    cont.append({"cont": c, "falls": o, "expected": round(e, 1), "ratio": round(o / e, 2), "area_pct": round(100 * g.area_km2.sum() / land, 1),
                 "falls_pct": round(100 * o / nl, 1), "pop_pct": round(100 * g.pop_est.sum() / T.pop_est.sum(), 1),
                 "per_10m": round(o / g.pop_est.sum() * 1e7, 2) if g.pop_est.sum() > 1e6 else None, "finds": int(g.finds.sum())})
cont.sort(key=lambda r: -r["falls"])
R["continents"] = {c["cont"]: c for c in cont}
R["continents_list"] = cont
R["ocean"] = {"land_pct": 29.2, "falls_per_land": round(70.8 / 29.2, 1)}   # Earth's surface: 29.2% land (standard figure)

# ---------- mass ----------
heavy = D.sort_values("mass_g", ascending=False).head(12)
R["heaviest"] = [{"name": r["name"], "t": round(r.mass_g / 1e6, 1), "fall": r.fall, "y": None if np.isnan(r.year) else int(r.year),
                  "cls": r.recclass, "group": r.group, "iso": r.iso, "country": M[r.iso]["name"] if r.iso else "", "lat": r.lat, "lon": r.lon, "id": int(r.id)}
                 for _, r in heavy.iterrows()]
hf = FALL.sort_values("mass_g", ascending=False).head(8)
R["heaviest_falls"] = [{"name": r["name"], "t": round(r.mass_g / 1e6, 2), "y": int(r.year), "cls": r.recclass, "country": M[r.iso]["name"]} for _, r in hf.iterrows()]
R["mass"] = {"median_fall": float(FALL.mass_g.median()), "median_find": float(FIND.mass_g.median()),
             "median_ant": reg["Antarctica"]["median_mass"], "median_rest_find": reg["Rest of the world"]["median_mass"],
             "median_sahara": reg["Sahara"]["median_mass"], "median_arabia": reg["Arabia"]["median_mass"],
             "top10_iron": int(sum(1 for h in R["heaviest"][:10] if h["group"] == "Iron")), "top10_found": int(sum(1 for h in R["heaviest"][:10] if h["fall"] == "Found")),
             "over_1t": int((D.mass_g >= 1e6).sum()), "under_100g_pct": pc((D.mass_g < 100).sum(), D.mass_g.notna().sum()),
             "total_t": round(D.mass_g.sum() / 1e6, 1), "top3_share": pc(heavy.head(3).mass_g.sum(), D.mass_g.sum())}
assert [h["name"] for h in R["heaviest"][:3]] == ["Hoba", "Cape York", "Campo del Cielo"]

# ---------- classes ----------
GN = [g for g, _ in GROUPS]
rest_find = FIND[FIND.region == "Rest of the world"]
cls = []
for g in GN:
    cls.append({"group": g, "n": int((D.group == g).sum()), "falls": int((FALL.group == g).sum()), "finds": int((FIND.group == g).sum()),
                "falls_pct": pc((FALL.group == g).sum(), len(FALL)), "finds_pct": pc((FIND.group == g).sum(), len(FIND)),
                "ant_pct": pc(((FIND.group == g) & (FIND.region == "Antarctica")).sum(), (FIND.region == "Antarctica").sum()),
                "hot_pct": pc(((FIND.group == g) & FIND.region.isin(hot)).sum(), FIND.region.isin(hot).sum()),
                "rest_pct": pc((rest_find.group == g).sum(), len(rest_find))})
R["classes"] = {c["group"]: c for c in cls}
R["classes_list"] = cls
R["classes_top"] = [{"cls": k, "n": int(v)} for k, v in D.recclass.value_counts().head(10).items()]
pd.DataFrame(cls).to_csv(f"{DATA}/classes.csv", index=False)
mars_moon = D[D.group.isin(["Martian", "Lunar"])]
R["mars_moon"] = {"martian": int((D.group == "Martian").sum()), "lunar": int((D.group == "Lunar").sum()),
                  "martian_falls": int((FALL.group == "Martian").sum()), "lunar_falls": int((FALL.group == "Lunar").sum()),
                  "desert_ice_pct": pc(mars_moon.region.isin(hot + ["Antarctica"]).sum(), len(mars_moon))}

# ---------- spotlight meteorites ----------
SPOT = ["Nogata", "Ensisheim", "Wold Cottage", "L'Aigle", "Sikhote-Alin", "Allende", "Murchison", "Peekskill", "Chelyabinsk",
        "Almahata Sitta", "Tissint", "Barwell", "Jilin", "Hoba", "Cape York", "Campo del Cielo", "Willamette", "Adelie Land", "Allan Hills 84001"]
R["spot"] = {}
for n in SPOT:
    r = D[D.name == n].iloc[0]
    R["spot"][n] = {"y": int(r.year), "fall": r.fall, "cls": r.recclass, "mass_g": float(r.mass_g), "country": M[r.iso]["name"] if r.iso else "Antarctica",
                    "lat": round(float(r.lat), 4), "lon": round(float(r.lon), 4), "id": int(r.id)}
R["uk"] = {"falls": int(fc.get("GBR", 0)), "finds": int(kc.get("GBR", 0))}
R["meta"] = {"page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "retrieved": RETRIEVED, "slug": SLUG, "boxes": REG["boxes"]}

# ---------- clean data out ----------
out = D0.copy()
out["country"] = out.iso.map(lambda i: M[i]["name"] if isinstance(i, str) and i in M else "")
out["year"] = out.year.astype("Int64")
out[["id", "name", "nametype", "recclass", "group", "fall", "mass_g", "year", "lat", "lon", "region", "region_from", "desert", "area", "iso", "country", "flag"]] \
    .rename(columns={"iso": "country_iso3", "area": "collection_area"}).to_csv(f"{DATA}/meteorites.csv", index=False)
pd.DataFrame(dec_rows).to_csv(f"{DATA}/decades.csv", index=False)
pd.DataFrame(R["areas"]).to_csv(f"{DATA}/collection_areas.csv", index=False)

# ---------- page data ----------
GI = {g: i for i, g in enumerate(GN)}; RI = {r: i for i, r in enumerate(REGN)}
P = D[loc].sort_values("mass_g", ascending=False, na_position="first")     # light first, heavy drawn last
P = P.iloc[::-1]
rowsP = [[round(r.lat, 4), round(r.lon, 4), int(r.year) if not np.isnan(r.year) else 0, -1 if np.isnan(r.mass_g) else (round(r.mass_g, 1) if r.mass_g < 1000 else int(round(r.mass_g))),
          1 if r.fall == "Fell" else 0, GI[r.group], RI[r.region], int(r.id), r["name"], r.recclass, r.iso or ""] for _, r in P.iterrows()]
jsave({"cols": ["lat", "lon", "year", "mass_g", "fell", "group", "region", "id", "name", "class", "iso"], "rows": rowsP}, f"{DATA}/points.json")
site = {"cname": {i: v["name"] for i, v in M.items()},
        "c": {r["iso"]: [r["falls"], r["finds"], r["expected"], r["ratio"], r["pop_est"], r["area_km2"]] for r in rows if r["falls"] or r["finds"] or r["expected"] > .5},
        "cpos": {i: [v["lx"], v["ly"], v["pop"]] for i, v in M.items()},
        "groups": GROUPS, "regions": REGIONS,
        "unloc": [[r["name"], int(r.year) if not np.isnan(r.year) else 0, r.recclass, r.fall, -1 if np.isnan(r.mass_g) else r.mass_g, int(r.id), r.region]
                  for _, r in D[~loc & ((D.mass_g >= 1000) | (D.fall == "Fell"))].iterrows()]}
jsave(site, f"{DATA}/site.json")
jsave(R, f"{DATA}/results.json", indent=1)
print("results ok; points", len(rowsP), os.path.getsize(f"{DATA}/points.json") // 1024, "KB; site", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
print({k: (v["n"], v["pct"]) for k, v in reg.items()}, R["hot"], R["icedesert"])
print(R["continents_list"]); print(R["countries"]["ratio_top"][:6], R["countries"]["ratio_low"][:5])
print(R["falls_time"], R["mass"], R["mars_moon"], R["countries"]["spearman"], R["countries"]["pearson_log"])
