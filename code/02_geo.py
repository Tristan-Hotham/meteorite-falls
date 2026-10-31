"""Geography: a light world outline file for the page and figures (Natural Earth 1:50m), and for every present-day
country its name, continent, rough population (Natural Earth POP_EST) and land area (geodesic area of the 1:10m
outline), plus city names for map labels."""
import numpy as np
from pyproj import Geod
from shapely.geometry import shape, mapping
from common import *

GEOD = Geod(ellps="WGS84")
iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]
FIX = {"CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "PSX": "PSE", "SAH": "ESH", "KAS": "IND", "SOL": "SOM"}


def rnd(c, k=2):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], k), round(c[1], k)]
    return [rnd(x, k) for x in c]


W50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
feats, meta = [], {}
for f in W50["features"]:
    p = f["properties"]; iso = FIX.get(iso_of(p), iso_of(p))
    g = shape(f["geometry"])
    gs = g.simplify(0.05, preserve_topology=True)
    if gs.is_empty:
        continue
    gm = mapping(gs)
    feats.append({"type": "Feature", "properties": {"iso": iso}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")

W10 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
for f in W10["features"]:
    p = f["properties"]; iso = FIX.get(iso_of(p), iso_of(p))
    g = shape(f["geometry"]).buffer(0)
    area = abs(GEOD.geometry_area_perimeter(g)[0]) / 1e6
    if iso in meta:                       # merged pieces (e.g. Cyprus): add area, keep the bigger one's name
        meta[iso]["area"] += area
        meta[iso]["pop"] += p["POP_EST"] or 0
        continue
    nm = (p["NAME_EN"] or p["NAME"]).replace("People's Republic of China", "China").replace("United States of America", "United States")
    cont = p["CONTINENT"]
    if cont == "Seven seas (open ocean)":
        cont = {"MUS": "Africa", "SYC": "Africa", "MDV": "Asia", "IOT": "Asia", "ATF": "Antarctica", "HMD": "Antarctica",
                "SHN": "Africa", "SGS": "Antarctica"}.get(iso, "Africa")
    meta[iso] = {"name": nm, "cont": cont, "pop": float(p["POP_EST"] or 0), "area": area,
                 "lx": round(p["LABEL_X"], 2), "ly": round(p["LABEL_Y"], 2)}
meta["CYP"]["name"] = "Cyprus"; meta["PSE"]["name"] = "Palestine"; meta["ESH"]["name"] = "Western Sahara"
for k in meta:
    meta[k]["area"] = round(meta[k]["area"], 1)
jsave(meta, f"{WORK}/countries.json")
tot = sum(v["area"] for v in meta.values())
print("countries", len(meta), "land area", round(tot / 1e6, 1), "million km2; Antarctica", round(meta["ATA"]["area"] / 1e6, 1))

P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")
cities = []
for f in P["features"]:
    p = f["properties"]; pop = p.get("pop_max") or 0
    if pop >= 150000 or p.get("adm0cap") == 1:
        cities.append({"name": re.sub(r"\s+", " ", p["name"]), "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop)})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
print("cities", len(cities), "world", os.path.getsize(f"{DATA}/world.json") // 1024, "KB")
