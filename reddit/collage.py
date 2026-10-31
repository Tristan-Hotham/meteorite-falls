"""r/dataisbeautiful collage for meteorite-falls: 2400 x 3000 px, light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
import matplotlib.patheffects as pe
import matplotlib.ticker as mt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
A, _ = points()
fell = A[A[:, 4] == 1]; found = A[A[:, 4] == 0]
BGc = "#F7F5F0"; SEAc = "#EAF0F3"
HALO = [pe.withStroke(linewidth=4, foreground=SEAc)]
CO = R["continents"]; C = R["countries"]

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGc)
fig.text(.045, .982, "Where space rocks land", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .922, f"Meteorites fall evenly over the Earth. People don't see them evenly. The {R['source']['falls']:,} meteorites that someone\nwatched fall cluster where people live and keep records; the {R['source']['finds']:,} found later come mostly from ice and desert.",
         fontproperties=SERP, fontsize=14.5, color=FG, va="top", linespacing=1.45)

# ---- main map: witnessed falls
ax = fig.add_axes([0, .522, 1, .32])
outline(ax, fc=SEAc, ec="#C9CDD0", lw=.8); world(ax, lw=.3, land="#E3DED2", ec=BGc)
x, y = proj(fell[:, 1], fell[:, 0])
sz = np.where(fell[:, 3] > 0, 6 + 5 * np.clip(np.log10(np.maximum(fell[:, 3], 1)) - 2, 0, 5), 7)
o = np.argsort(-sz)
ax.scatter(x[o], y[o], s=sz[o], c=FALL, lw=.4, edgecolor="#6a1f05", alpha=.9, zorder=4)
fig.text(.045, .846, "Witnessed falls", fontproperties=DISPB, fontsize=19, color=FALL, va="bottom")
fig.text(.255, .848, "each dot a meteorite seen to fall, sized by weight; × = falls against an even share of the land", fontsize=9.5, color=MUT, va="bottom")
LAB = [  # lon, lat in open sea; text; alignment
    (-41, 43, f"EUROPE\n{CO['Europe']['falls']} falls, {CO['Europe']['ratio']:.1f}×", "center"),
    (150, 19, f"JAPAN\n{C['JPN']['falls']} falls, {C['JPN']['ratio']:.0f}×", "center"),
    (89, -16, f"INDIA\n{C['IND']['falls']} falls, {C['IND']['ratio']:.1f}×", "center"),
    (-130, 32, f"NORTH AMERICA\n{CO['North America']['falls']} falls, {CO['North America']['ratio']:.1f}×", "right"),
    (-23, -28, f"AFRICA\n{CO['Africa']['falls']} falls, {CO['Africa']['ratio']:.1f}×", "center"),
    (-108, -25, f"SOUTH AMERICA\n{CO['South America']['falls']} falls, {CO['South America']['ratio']:.1f}×", "center"),
    (98, -40, f"OCEANIA\n{CO['Oceania']['falls']} falls, {CO['Oceania']['ratio']:.1f}×", "center"),
    (25, -54, f"ANTARCTICA\n0 falls, {CO['Antarctica']['expected']:.0f} expected", "center")]
for lon, lat, t, ha in LAB:
    X, Y = proj(lon, lat)
    ax.text(X, Y, t, ha=ha, va="center", fontsize=10, color=FG, family=MONO, linespacing=1.25, zorder=6, path_effects=HALO, fontweight="medium")

# ---- numbers row
nums = [(f"{R['regions']['Antarctica']['pct']:.0f}%", RCOL["Antarctica"], "of all known meteorites\nwere found on Antarctic\nice; none seen to fall"),
        (f"{R['hot']['pct']:.0f}%", RCOL["Sahara"], "were found in hot\ndeserts: the Sahara,\nOman and others"),
        (f"{R['source']['falls_pct']:.1f}%", FALL, f"were witnessed falls\n({R['source']['falls']:,}), {R['rest']['falls_pct']:.0f}% of them\noutside ice and desert"),
        (f"{C['JPN']['ratio']:.0f}×", "#5B4A8B", "Japan's share of falls\ncompared with an even\nspread over the land")]
for i, (big, col, small) in enumerate(nums):
    xx = .045 + i * .235
    fig.text(xx, .515, big, fontproperties=DISP, fontsize=38, color=col, va="top")
    fig.text(xx, .472, small, family=MONO, fontsize=10.5, color=FG, va="top", linespacing=1.4)

# ---- finds insets: Antarctica (polar) and Sahara + Arabia
fig.text(.045, .395, "Finds: where people look", fontproperties=DISPB, fontsize=19, color=FG, va="bottom")
fig.text(.40, .3975, "circle area: meteorites per half-degree square", fontsize=10.5, color=MUT, va="bottom")
a1 = ant_inset(fig, [.035, .262, .3, .128], found, k=.7)
a1.text(.5, -.04, f"Antarctica: {R['regions']['Antarctica']['n']:,} finds", transform=a1.transAxes, ha="center", va="top", fontsize=11, color=FG)
a2 = fig.add_axes([.37, .266, .6, .124])
ext = (*proj(-18, 15)[0:1], *proj(61, 15)[0:1])
x0, _ = proj(-18, 24); x1, _ = proj(61, 24); _, y0 = proj(20, 11); _, y1 = proj(20, 37.5)
world(a2, lw=.4, land="#E3DED2", ec=BGc, ext=(x0, x1, y0, y1))
a2.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=SEAc, ec="none", zorder=0))
for ri, r in ((1, "Sahara"), (2, "Arabia"), (4, "Rest of the world")):
    s = found[found[:, 6] == ri]
    la, lo, n = stacks(s, .5); X, Y = proj(lo, la); o = np.argsort(-n)
    a2.scatter(X[o], Y[o], s=.9 * (2 + 3 * np.sqrt(n[o])), c=RCOL[r], alpha=.65, lw=.3, edgecolor="#fff", zorder=3)
fx, fy = proj(fell[:, 1], fell[:, 0])
a2.scatter(fx, fy, s=10, c=FALL, lw=.4, edgecolor="#6a1f05", zorder=4)
a2.text(.5, -.04, f"Sahara and Arabia: {R['regions']['Sahara']['n'] + R['regions']['Arabia']['n']:,} finds, {R['regions']['Sahara']['falls'] + R['regions']['Arabia']['falls']} falls", transform=a2.transAxes, ha="center", va="top", fontsize=11, color=FG)
for sp in a2.spines.values(): sp.set_visible(False)

# ---- charts
D = [d for d in R["decades"] if d["dec"] < 2010]
b1 = fig.add_axes([.075, .09, .40, .084]); b1.set_facecolor(BGc)
b1.bar([d["dec"] for d in D], [d["falls"] for d in D], width=8, color=FALL)
b1.set_xticks([1800, 1850, 1900, 1950, 2000]); b1.set_xticklabels(["1800s", "1850s", "1900s", "1950s", "2000s"]); b1.tick_params(labelsize=9.5); spines(b1)
b1.set_title("Witnessed falls per decade", family=MONO, fontsize=12.5, color=FG, loc="left", pad=8)
b1.annotate(f"peak: {R['falls_time']['peak_n']} in the {R['falls_time']['peak_dec']}s", (R["falls_time"]["peak_dec"], R["falls_time"]["peak_n"]), xytext=(1810, 85), fontsize=9.5, color=FG, va="center",
            arrowprops=dict(arrowstyle="-", color=MUT, lw=.7))
b2 = fig.add_axes([.60, .09, .36, .084]); b2.set_facecolor(BGc)
T = [c for c in SITE["c"].values() if c[0] > 0 and c[5] >= 20000 and c[4] > 0]
px = np.array([c[4] / c[5] for c in T]); fy2 = np.array([c[0] / c[5] * 1e6 for c in T])
b2.scatter(px, fy2, s=14, c=FALL, alpha=.6, lw=.4, edgecolor="#fff"); b2.set_xscale("log"); b2.set_yscale("log"); spines(b2); b2.tick_params(labelsize=9.5)
for a in (b2.xaxis, b2.yaxis): a.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:g}"))
b2.set_xlabel("people per km²", fontsize=9.5); b2.set_ylabel("falls per\nmillion km²", fontsize=9.5)
b2.set_title("Falls against people, by country", family=MONO, fontsize=12.5, color=FG, loc="left", pad=8)
b2.text(.03, .95, f"r = {R['countries']['pearson_log']:.2f} (log scales)", transform=b2.transAxes, fontsize=9.5, color=MUT, va="top")

LEGP = SERP.copy(); LEGP.set_size(12)
H = [Line2D([], [], ls="", marker="o", ms=8, mfc=FALL, mec="#6a1f05", label="Witnessed fall"),
     Line2D([], [], ls="", marker="o", ms=10, mfc=RCOL["Antarctica"], mec="none", alpha=.7, label="Find: Antarctic ice"),
     Line2D([], [], ls="", marker="o", ms=10, mfc=RCOL["Sahara"], mec="none", alpha=.7, label="Find: Sahara"),
     Line2D([], [], ls="", marker="o", ms=10, mfc=RCOL["Arabia"], mec="none", alpha=.7, label="Find: Arabia (mostly Oman)"),
     Line2D([], [], ls="", marker="o", ms=10, mfc=RCOL["Rest of the world"], mec="none", alpha=.7, label="Find: rest of the world")]
fig.legend(handles=H, loc="upper left", bbox_to_anchor=(.035, .247), ncol=3, frameon=False, prop=LEGP, handletextpad=.3, columnspacing=1.4)
fig.text(.045, .01, f"Source: The Meteoritical Society, Meteoritical Bulletin Database, via NASA's Open Data Portal (Meteorite Landings, records to {R['source']['last_year']}); Natural Earth.\n"
         "Even share: each country's share of land area, Antarctica included. Many ice and desert finds are fragments of one fall named separately.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib  ·  maps.tristanhotham.com/meteorite-falls", family=MONO, fontsize=8.6, color=MUT, linespacing=1.5, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "where_space_rocks_land.png")
fig.savefig(out, facecolor=BGc, dpi=200)
print("ok", out)
