# Where space rocks land

A map of 45,715 meteorites recovered on Earth, from the Meteoritical Society's Meteoritical Bulletin Database as published by NASA ("Meteorite Landings", records to 2013). It separates the 1,107 witnessed falls from the 44,608 finds and shows why the record is so lumpy: finds come mostly from Antarctic ice and hot deserts, where meteorites are easy to see and slow to weather, while witnessed falls follow people.

Interactive page: https://maps.tristanhotham.com/meteorite-falls/
Paper: https://doi.org/10.5281/zenodo.23847548
Blog post: https://blog.tristanhotham.com/2026/10/31/meteorite-falls/

## Headline results

- Ice and desert: 65% of all records (29,783) come from Antarctica and 24% (10,822) from hot deserts (Sahara 15%, Arabia 7%). Together 89%. The rest of the world supplies 8%.
- Falls: only 2.4% of meteorites were seen to fall; 96% of those are outside the ice and desert areas, and none is in Antarctica (an even spread over the land would give it about 92).
- Falls follow people: against an even spread over the land, Europe records 2.2 times its share, Africa 0.6, South America 0.4, Oceania 0.3. Japan 15 times, Italy 14, France 13, Germany 12, the UK 10. Correlation of falls per km² with people per km² (log scales, 106 countries): 0.62.
- Time: witnessed falls rose from 17 in the 1800s to 91 in the 1930s and have held at about 59 a decade since; finds exploded after the Yamato discovery of 1969, peaking at 17,697 in the 2000s.
- Mass and class: the heaviest are Hoba (60 t), Cape York (58.2 t) and Campo del Cielo (50 t), all iron finds. Irons are 4.4% of falls but 27% of finds outside ice and desert. Median Antarctic find: 13.4 g.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; page data embedded, `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/meteorites.csv` | All 45,716 records, cleaned: Bulletin id, name, class, broad group, fell or found, mass, year, coordinates, recovery region (and whether it came from the point or the name), collection area, present-day country, flags. |
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
- Places: missing or 0°, 0° coordinates are unknown (13,529 records). Regions: Antarctica south of 60°S; rough boxes for the Sahara, Arabia, the Atacama and the Australian deserts; otherwise the rest of the world. Records without a point take the region of their collection area (the name before the number) when 80% of that area's located meteorites share one (11,990 records).
- Even spread: each country's expected falls = witnessed falls with a country x its share of land area (Natural Earth, Antarctica included). Population is Natural Earth's POP_EST, a rough present-day estimate.
- Caveats: the table ends in 2013; many Antarctic and desert records are fragments of one fall named separately; finds have a year of finding, not of falling; desert boxes are coarse; population is today's, not historical.

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

Hotham, T. (2026) Where space rocks land: falls, finds and the geography of the meteorite record. Zenodo. https://doi.org/10.5281/zenodo.23847548

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
