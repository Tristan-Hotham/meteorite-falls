"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, rg, co, c, k = R["source"], R["regions"], R["continents"], R["countries"], R["classes"]
N = lambda v: f"{round(v):,}"
readme = f"""# Where space rocks land

A map of {N(s['n'])} meteorites recovered on Earth, from the Meteoritical Society's Meteoritical Bulletin Database as published by NASA ("Meteorite Landings", records to {s['last_year']}). It separates the {N(s['falls'])} witnessed falls from the {N(s['finds'])} finds and shows why the record is so lumpy: finds come mostly from Antarctic ice and hot deserts, where meteorites are easy to see and slow to weather, while witnessed falls follow people.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- Ice and desert: {rg['Antarctica']['pct']:.0f}% of all records ({N(rg['Antarctica']['n'])}) come from Antarctica and {R['hot']['pct']:.0f}% ({N(R['hot']['n'])}) from hot deserts (Sahara {rg['Sahara']['pct']:.0f}%, Arabia {rg['Arabia']['pct']:.0f}%). Together {R['icedesert']['pct']:.0f}%. The rest of the world supplies {rg['Rest of the world']['pct']:.0f}%.
- Falls: only {s['falls_pct']:.1f}% of meteorites were seen to fall; {R['rest']['falls_pct']:.0f}% of those are outside the ice and desert areas, and none is in Antarctica (an even spread over the land would give it about {co['Antarctica']['expected']:.0f}).
- Falls follow people: against an even spread over the land, Europe records {co['Europe']['ratio']:.1f} times its share, Africa {co['Africa']['ratio']:.1f}, South America {co['South America']['ratio']:.1f}, Oceania {co['Oceania']['ratio']:.1f}. Japan {c['JPN']['ratio']:.0f} times, Italy {c['ITA']['ratio']:.0f}, France {c['FRA']['ratio']:.0f}, Germany {c['DEU']['ratio']:.0f}, the UK {c['GBR']['ratio']:.0f}. Correlation of falls per km² with people per km² (log scales, {c['n_big_falls']} countries): {c['pearson_log']:.2f}.
- Time: witnessed falls rose from {R['falls_time']['d1800']} in the 1800s to {R['falls_time']['peak_n']} in the {R['falls_time']['peak_dec']}s and have held at about {R['falls_time']['since1950_mean']:.0f} a decade since; finds exploded after the Yamato discovery of {R['antarctic']['yamato']['y']}, peaking at {N(R['finds_time']['peak_n'])} in the {R['finds_time']['peak_dec']}s.
- Mass and class: the heaviest are Hoba ({R['heaviest'][0]['t']:.0f} t), Cape York ({R['heaviest'][1]['t']:.1f} t) and Campo del Cielo ({R['heaviest'][2]['t']:.0f} t), all iron finds. Irons are {k['Iron']['falls_pct']:.1f}% of falls but {k['Iron']['rest_pct']:.0f}% of finds outside ice and desert. Median Antarctic find: {R['mass']['median_ant']:.1f} g.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; page data embedded, `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/meteorites.csv` | All {N(s['n_rows'])} records, cleaned: Bulletin id, name, class, broad group, fell or found, mass, year, coordinates, recovery region (and whether it came from the point or the name), collection area, present-day country, flags. |
| `data/countries.csv` | Per country: witnessed falls, finds, land area, population estimate, falls expected from an even spread, ratio, falls per million km² and per 10 million people. |
| `data/decades.csv` | Witnessed falls, and finds by region, per decade from the 1800s. |
| `data/classes.csv` | Broad classes among falls, finds, Antarctic, hot desert and other finds. |
| `data/collection_areas.csv` | The largest collection areas. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots of the page at desktop and phone widths. |

## Method in brief

- Data: NASA's Meteorite Landings table, from a GitHub mirror, checked cell by cell against a second independent mirror (identical apart from three loosely dated archaeological finds) and a third five-column copy. Meridiani Planum (found on Mars) left out. One future year set to missing.
- Places: missing or 0°, 0° coordinates are unknown ({N(s['unlocated'])} records). Regions: Antarctica south of 60°S; rough boxes for the Sahara, Arabia, the Atacama and the Australian deserts; otherwise the rest of the world. Records without a point take the region of their collection area (the name before the number) when 80% of that area's located meteorites share one ({N(s['region_from_name'])} records).
- Even spread: each country's expected falls = witnessed falls with a country x its share of land area (Natural Earth, Antarctica included). Population is Natural Earth's POP_EST, a rough present-day estimate.
- Caveats: the table ends in {s['last_year']}; many Antarctic and desert records are fragments of one fall named separately; finds have a year of finding, not of falling; desert boxes are coarse; population is today's, not historical.

## How to rerun

Needs Python 3 with numpy, pandas, scipy, shapely, pyproj, matplotlib and fontTools, xelatex and pdftotext; node with Playwright for `code/qa.js`. Raw inputs are read in place (paths in `code/common.py`): the meteorite CSV mirrors in `/home/claude/newdata/raw/meteorites/`, Natural Earth files in `/home/claude/newdata/raw/geo/` and the World Bank population file. Intermediate files go to `/dev/shm/meteorites/work` (set `METTMP` to change).

```
python3 code/01_clean.py        # check copies, clean, regions, classes, countries
python3 code/02_geo.py          # outlines, areas, population, city labels
python3 code/03_results.py      # results.json, data tables, page data
python3 code/04_build_site.py   # index.html
python3 code/05_figures.py      # header, blog and paper figures
python3 code/06_paper.py        # paper PDF
python3 reddit/collage.py       # collage
python3 code/07_readme.py       # README, LICENSE, Reddit post
python3 code/08_release.py      # blog post, Zenodo files
```

## Sources and licences

- The Meteoritical Society, Meteoritical Bulletin Database (https://www.lpi.usra.edu/meteor/), as published by NASA's Open Data Portal as "Meteorite Landings" (https://data.nasa.gov/, dataset gh4g-9sfh), NASA open data. Copies used: https://github.com/stefmolin/pandas-workshop (data/Meteorite_Landings.csv) and https://github.com/hi-primus/optimus (examples/data/Meteorite_Landings.csv), with https://github.com/openlayers/openlayers (examples/data/csv/meteorite_landings.csv) as a further check.
- Natural Earth countries and populated places (https://www.naturalearthdata.com/). Public domain.
- World Bank, Population, total (CC BY 4.0), for the change in world population from the 1960s to the 2000s.
- Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Where space rocks land: falls, finds and the geography of the meteorite record. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post, the figures and the derived data
files in data/ are released under CC BY 4.0. The meteorite records are derived
from the Meteoritical Society's Meteoritical Bulletin Database as published by
NASA's Open Data Portal; please credit both. Natural Earth is public domain;
World Bank data are CC BY 4.0.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""## Title

[OC] {rg['Antarctica']['pct']:.0f}% of the world's known meteorites were found in Antarctica, where nobody has ever seen one fall. The {N(s['falls'])} witnessed falls follow people instead

## Body

I mapped all {N(s['n'])} meteorites in NASA's copy of the Meteoritical Society's catalogue (records to {s['last_year']}). Meteorites land more or less evenly over the planet, but the record is lumpy: {rg['Antarctica']['pct']:.0f}% come from Antarctic blue ice and {R['hot']['pct']:.0f}% from hot deserts (the Sahara and Oman especially), because dark stones are easy to spot there and barely weather. Only {s['falls_pct']:.1f}% were actually seen to fall, and those cluster where people live and keep records: Japan has {c['JPN']['ratio']:.0f} times its share of falls by land area, and Italy, France, Germany and the UK more than 10 times; Antarctica would expect about {co['Antarctica']['expected']:.0f} and has none. Caveats: many ice and desert finds are fragments of a single fall; population is a rough present-day estimate. Interactive map with falls/finds toggle, year and class filters: {PAGE}

## Source comment

Source: The Meteoritical Society, Meteoritical Bulletin Database, as published by NASA's Open Data Portal ("Meteorite Landings", records to {s['last_year']}), checked against two GitHub mirrors; Natural Earth outlines, land areas and population estimates (public domain). "Even share" = each country's share of the world's land area (Antarctica included). Antarctica = south of 60°S; hot deserts = rough boxes around the Sahara, Arabia, the Atacama and the Australian deserts.

Tools: Python (pandas, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
for t in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("readme, licence, post ok")
