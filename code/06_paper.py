"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them)."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_Space_Rocks_Land"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# checks for statements made in words in the paper only
M = pd.read_csv(f"{DATA}/meteorites.csv")
icedes = M[M.region.isin(["Antarctica", "Sahara", "Arabia", "Other hot deserts"])]
assert (icedes.year < 1969).sum() / len(icedes) < .02          # "almost all of it collected since 1969"
assert R["falls_time"]["falls_change_pct"] < 0


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "pc1": return f"{float(v):.1f}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


rows = ""
for r, _ in REGIONS:
    g = R["regions"][r]
    rows += f"{r} & {g['n']:,} & {g['pct']:.1f}\\% & {g['finds']:,} & {g['falls']:,} & {g['from_name']:,}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Meteorites by recovery region. `From name': placed by collection area because the record has no point.}\\label{tab:reg}"
      "\\begin{tabular}{lrrrrr}\\toprule Region & Meteorites & Share & Finds & Falls & From name\\\\\\midrule\n" + rows +
      f"\\midrule All & {R['source']['n']:,} & 100\\% & {R['source']['finds']:,} & {R['source']['falls']:,} & {R['source']['region_from_name']:,}\\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
rows = "".join(f"{tex(a['area'])} & {tex(a['region'])} & {a['n']:,} & {a['first'] or ''}\\\\\n" for a in R["areas"][:15])
TA = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen largest collection areas (name before the number) and the first year recorded.}\\label{tab:areas}"
      "\\begin{tabular}{llrr}\\toprule Collection area & Region & Meteorites & First year\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{c['cont']} & {c['area_pct']:.1f}\\% & {c['pop_pct']:.1f}\\% & {c['falls']} & {c['expected']:.1f} & {c['ratio']:.2f}\\\\\n" for c in R["continents_list"])
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Witnessed falls by continent against an even spread over the land. Population: Natural Earth estimate.}\\label{tab:cont}"
      "\\begin{tabular}{lrrrrr}\\toprule Continent & Land & People & Falls & Expected & Ratio\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(c['name'])} & {c['falls']} & {c['expected']:.1f} & {c['ratio']:.2f}\\\\\n" for c in R["countries"]["top"])
TK = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen countries with most witnessed falls, with falls expected from land area.}\\label{tab:countries}"
      "\\begin{tabular}{lrrr}\\toprule Country & Falls & Expected & Ratio\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(h['name'])} & {tex(h['country'])} & {h['t']:.1f} & {tex(h['cls'])} & {'fell' if h['fall'] == 'Fell' else 'found'} {h['y'] or ''}\\\\\n" for h in R["heaviest"][:12])
TH = ("\\begin{table}[tbp]\\centering\\small\\caption{The twelve heaviest meteorites by total recovered mass.}\\label{tab:heavy}"
      "\\begin{tabular}{llrll}\\toprule Meteorite & Country & Tonnes & Class & Year\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|meta\.doi)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("REGIONS", TR), ("AREAS", TA), ("CONT", TC), ("COUNTRIES", TK), ("HEAVY", TH)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = t.replace("{{meta.doi}}", "10.5281/zenodo.23847548")
assert "{{" not in t.replace("10.5281/zenodo.23847548", "") and "--" not in t and "\u2014" not in t and "\u2013" not in t
t = t.replace("\\href{https://doi.org/10.5281/zenodo.23847548}{https://doi.org/10.5281/zenodo.23847548}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/10.5281/zenodo.23847548}", "https://doi.org/\\{\\{DOI\\}\\}")
assert "{{" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
