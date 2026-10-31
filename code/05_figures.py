"""Header card, blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png)."""
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mt
from figstyle import *

R = jload(f"{DATA}/results.json")
A, P = points()
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
os.makedirs(BL, exist_ok=True); os.makedirs(PA, exist_ok=True)
REGN = [r for r, _ in REGIONS]; GN = [g for g, _ in GROUPS]
fell = A[A[:, 4] == 1]; found = A[A[:, 4] == 0]


def both(fig, name):
    fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def fall_dots(ax, rows, s=9, z=4):
    x, y = proj(rows[:, 1], rows[:, 0])
    ax.scatter(x, y, s=s, c=FALL, lw=.35, edgecolor="#5a1a06", zorder=z, alpha=.9)


def find_stacks(ax, rows, k=1.6, z=3, cell=0.5, alpha=.6):
    for ri, r in enumerate(REGN):
        s = rows[rows[:, 6] == ri]
        if not len(s): continue
        la, lo, n = stacks(s, cell)
        x, y = proj(lo, la)
        o = np.argsort(-n)
        ax.scatter(x[o], y[o], s=k * (2 + 3 * np.sqrt(n[o])), c=RCOL[r], lw=.3, edgecolor="#ffffff", alpha=alpha, zorder=z)


def size_key(fig, rect, k, col="#8A8F96", label="finds in a half-degree square"):
    ax = fig.add_axes(rect); ax.axis("off")
    for i, n in enumerate((1, 10, 100, 1000)):
        ax.scatter([i], [0], s=k * (2 + 3 * np.sqrt(n)), c=col, alpha=.6, lw=.3, edgecolor="#fff")
        ax.text(i, -.9, f"{n:,}", ha="center", fontsize=9.5, color=MUT)
    ax.set_xlim(-.6, 3.6); ax.set_ylim(-1.3, 1)
    if label: ax.set_title(label, fontsize=9.5, color=MUT, loc="left", pad=2)


# 1. two maps: witnessed falls, finds
fig = plt.figure(figsize=(12, 12.4), facecolor=BG)
ax = fig.add_axes([0, .53, 1, .43]); outline(ax, fc=SEA, ec="#C9CDD0"); world(ax, lw=.25)
fall_dots(ax, fell, s=8)
ax.text(.01, 1.03, f"Witnessed falls: {R['source']['falls_located']:,} with a place", transform=ax.transAxes, fontproperties=DISPB, fontsize=19, color=FALL)
ax2 = fig.add_axes([0, .05, 1, .43]); outline(ax2, fc=SEA, ec="#C9CDD0"); world(ax2, lw=.25)
find_stacks(ax2, found, k=1.1)
ax2.text(.01, 1.03, f"Finds: {R['source']['finds_located']:,} with a place", transform=ax2.transAxes, fontproperties=DISPB, fontsize=19, color=FG)
ant_inset(fig, [.005, .06, .2, .2], found, k=.7, title="Antarctica seen from above")
fig.legend(handles=[Patch(fc=RCOL[r], ec="none", label=r) for r in REGN[:5]], loc="lower left", bbox_to_anchor=(.02, .005), ncol=5, frameon=False, fontsize=10, handlelength=1)
size_key(fig, [.80, .005, .19, .04], 1.1, label="")
fig.text(.795, .03, "finds per\nhalf-degree\nsquare:", ha="right", va="center", fontsize=9, color=MUT)
both(fig, "maps")

# 2. regions: all, finds, falls (100% stacked)
fig, ax = plt.subplots(figsize=(11, 3.6), facecolor=BG); ax.set_facecolor(BG)
rows = [("All records", "n", R["source"]["n"]), ("Finds", "finds", R["source"]["finds"]), ("Witnessed falls", "falls", R["source"]["falls"])]
for i, (lab, k, tot) in enumerate(rows):
    left = 0
    for r in REGN:
        v = 100 * R["regions"][r][k] / tot
        ax.barh(2 - i, v, left=left, color=RCOL[r], height=.66, edgecolor=BG, lw=.6)
        if v >= 5: ax.text(left + 1, 2 - i, f"{v:.0f}%", va="center", fontsize=11, color="#fff", fontweight="medium")
        left += v
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([f"{l}\n{t:,}" for l, _, t in rows], fontsize=11)
ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0f}%")); spines(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.legend(handles=[Patch(fc=RCOL[r], label=r) for r in REGN], ncol=6, loc="upper center", bbox_to_anchor=(.45, -.14), frameon=False, fontsize=10, handlelength=1, columnspacing=1)
fig.tight_layout()
both(fig, "regions")

# 3. decades
D = R["decades"]
fig, ax = plt.subplots(figsize=(11, 5.6), facecolor=BG); ax.set_facecolor(BG)
xs = np.arange(len(D)); b = np.zeros(len(D))
for r in REGN:
    v = np.array([d[r] for d in D]); ax.bar(xs, v, bottom=b, color=RCOL[r], width=.82, label=f"finds: {r}"); b += v
ax.set_xticks(xs[::2]); ax.set_xticklabels([f"{d['dec']}s" for d in D][::2], fontsize=10)
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{int(v):,}")); ax.set_ylabel("finds per decade"); spines(ax)
ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
a2 = ax.twinx(); a2.plot(xs[:-1], [d["falls"] for d in D[:-1]], color=FALL, lw=2.4, marker="o", ms=4, label="witnessed falls (right scale)")
a2.plot(xs[-1:], [D[-1]["falls"]], "o", mfc="none", mec=FALL, ms=6)
a2.set_ylim(0, 100); a2.set_ylabel("witnessed falls per decade", color=FALL); a2.tick_params(axis="y", colors=FALL); a2.spines["top"].set_visible(False); a2.spines["right"].set_color(FALL)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
ax.legend(h2 + h1, l2 + l1, loc="upper left", frameon=False, fontsize=10)
ax.text(len(D) - 1.6, 4000, "2010s:\nto 2013\nonly", ha="center", fontsize=9, color=MUT)
fig.tight_layout()
both(fig, "decades")

# 4. continents against an even spread
C = R["continents_list"]
fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
ys = np.arange(len(C))[::-1]
ax.barh(ys, [c["falls"] for c in C], color=[FALL if c["ratio"] >= 1 else LESS for c in C], height=.62)
for y, c in zip(ys, C):
    ax.plot([c["expected"]] * 2, [y - .42, y + .42], color=FG, lw=2.6)
    ax.text(max(c["falls"], c["expected"]) + 6, y, f"{c['falls']} falls, {c['expected']:.0f} expected ({c['ratio']:.1f}×)", va="center", fontsize=10)
ax.set_yticks(ys); ax.set_yticklabels([c["cont"] for c in C], fontsize=11); ax.set_xlim(0, 560); spines(ax)
ax.set_xlabel("witnessed falls; black tick = expected if spread evenly over the land")
fig.tight_layout()
both(fig, "continents")

# 5. country ratios
top, low = R["countries"]["ratio_top"], R["countries"]["ratio_low"]
rows = top + low
fig, ax = plt.subplots(figsize=(10, 8.2), facecolor=BG); ax.set_facecolor(BG)
ys = np.arange(len(rows))[::-1].astype(float); ys[len(top):] -= .6
nm = lambda s: s.replace("Democratic Republic of the Congo", "DR Congo")
for y, r in zip(ys, rows):
    v = max(r["ratio"], .012)
    ax.barh(y, np.log10(v), color=FALL if r["ratio"] >= 1 else LESS, height=.7)
    ax.text(np.log10(v) + (.04 if v >= 1 else -.04), y, f"{r['falls']} / {r['expected']:.1f}", va="center", ha="left" if v >= 1 else "right", fontsize=9.5)
ax.axvline(0, color=FG, lw=1.2)
ax.set_yticks(ys); ax.set_yticklabels([nm(r["name"]) for r in rows], fontsize=10)
ax.set_xticks([-2, -1, 0, 1]); ax.set_xticklabels(["0.01", "0.1", "1 (even)", "10"]); ax.set_xlim(-2.3, 1.55)
ax.set_xlabel("witnessed falls ÷ falls expected from land area (log scale); labels: falls / expected")
ax.axhline(ys[len(top)] + .8, color=MUT, lw=.8, ls=(0, (3, 3))); spines(ax)
fig.tight_layout()
both(fig, "ratio")

# 6. falls and people
T = [r for r in jload(f"{DATA}/site.json")["c"].items() if r[1][0] > 0 and r[1][5] >= 20000 and r[1][4] > 0]
CN = jload(f"{DATA}/site.json")["cname"]
fig, ax = plt.subplots(figsize=(10, 6.6), facecolor=BG); ax.set_facecolor(BG)
px = np.array([c[4] / c[5] for _, c in T]); fy = np.array([c[0] / c[5] * 1e6 for _, c in T]); n = np.array([c[0] for _, c in T])
ax.scatter(px, fy, s=12 + 6 * n ** .8 / 2, c=FALL, alpha=.55, lw=.6, edgecolor="#fff")
SHOW = {"JPN": "Japan", "ITA": "Italy", "FRA": "France", "DEU": "Germany", "GBR": "UK", "IND": "India", "USA": "US", "CHN": "China", "RUS": "Russia",
        "CAN": "Canada", "BRA": "Brazil", "AUS": "Australia", "BGD": "Bangladesh", "DZA": "Algeria", "NGA": "Nigeria", "MNG": "Mongolia"}
for (iso, c), x, y in zip(T, px, fy):
    if iso in SHOW:
        ax.annotate(SHOW[iso], (x, y), xytext=(6, 4) if iso not in ("DEU", "BGD") else (-6, 6), textcoords="offset points", fontsize=9.5, ha="left" if iso not in ("DEU", "BGD") else "right")
ax.set_xscale("log"); ax.set_yscale("log"); spines(ax); ax.grid(color=RULE, lw=.7); ax.set_axisbelow(True)
ax.set_xlabel("people per km² (Natural Earth estimate)"); ax.set_ylabel("witnessed falls per million km²")
for a in (ax.xaxis, ax.yaxis): a.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:g}"))
ax.text(.02, .97, f"{len(T)} countries over 20,000 km² with at least one fall.\nCorrelation on log scales: {R['countries']['pearson_log']:.2f}.", transform=ax.transAxes, va="top", fontsize=10, color=MUT)
fig.tight_layout()
both(fig, "people")

# 7. classes
K = R["classes_list"]
fig, ax = plt.subplots(figsize=(11, 4.3), facecolor=BG); ax.set_facecolor(BG)
rows = [("Witnessed falls", "falls_pct"), ("Antarctic finds", "ant_pct"), ("Hot desert finds", "hot_pct"), ("Finds elsewhere", "rest_pct")]
for i, (lab, k) in enumerate(rows):
    left = 0
    for c in K:
        v = c[k]; ax.barh(3 - i, v, left=left, color=GCOL[c["group"]], height=.66, edgecolor=BG, lw=.5)
        if v >= 5: ax.text(left + 1, 3 - i, f"{v:.0f}%", va="center", fontsize=10.5, color="#fff")
        left += v
ax.set_yticks([3, 2, 1, 0]); ax.set_yticklabels([r[0] for r in rows], fontsize=11); ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0f}%")); spines(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.legend(handles=[Patch(fc=c, label=g) for g, c in GROUPS], ncol=5, loc="upper center", bbox_to_anchor=(.42, -.13), frameon=False, fontsize=9.5, handlelength=1, columnspacing=1)
fig.tight_layout()
both(fig, "classes")

# 8. (paper) masses by region
fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=BG); ax.set_facecolor(BG)
bins = np.logspace(-1, 8, 46)
sets = [("Antarctic finds", found[(found[:, 6] == 0) & (found[:, 3] > 0), 3], RCOL["Antarctica"]),
        ("Hot desert finds", found[np.isin(found[:, 6], [1, 2, 3]) & (found[:, 3] > 0), 3], RCOL["Sahara"]),
        ("Finds elsewhere", found[(found[:, 6] == 4) & (found[:, 3] > 0), 3], RCOL["Rest of the world"]),
        ("Witnessed falls", fell[fell[:, 3] > 0, 3], FALL)]
for lab, v, c in sets:
    h, e = np.histogram(v, bins); ax.step(e[:-1], h / h.sum() * 100, where="post", color=c, lw=2, label=lab)
ax.set_xscale("log"); ax.set_xlabel("recovered weight (g, log scale)"); ax.set_ylabel("% of group"); spines(ax)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: {.1: "0.1 g", 1: "1 g", 10: "10 g", 100: "100 g", 1e3: "1 kg", 1e4: "10 kg", 1e5: "100 kg", 1e6: "1 t", 1e7: "10 t", 1e8: "100 t"}.get(v, "")))
ax.legend(frameon=False, fontsize=10); fig.tight_layout()
fig.savefig(os.path.join(PA, "f_mass.png"), dpi=200, facecolor=BG); plt.close(fig)

# 9. (paper) Antarctica close up
fig = plt.figure(figsize=(8, 8), facecolor=BG); ax = fig.add_axes([0, 0, 1, .93])
ax.add_patch(plt.Circle((0, 0), SP.transform(0, -60)[1] * -1, fc=SEA, ec="#C9CDD0", zorder=0))
antarctica(ax, lat_min=-60)
s = found[found[:, 6] == 0]; la, lo, n = stacks(s, .5); x, y = SP.transform(lo, la)
o = np.argsort(-n); ax.scatter(x[o], y[o], s=4 + 5 * np.sqrt(n[o]), c=RCOL["Antarctica"], alpha=.6, lw=.4, edgecolor="#fff", zorder=3)
for nm_, lon, lat, dx, dy in (("Yamato", 35.67, -71.5, 0, 1.0e6), ("Allan Hills", 159.67, -76.72, 1.0e6, .5e6), ("Queen Alexandra Range", 168, -84, .2e6, -1.2e6), ("Grove Mountains", 75.3, -72.8, 1.1e6, .3e6), ("Asuka", 24.3, -72, -.8e6, 1.0e6)):
    X, Y = SP.transform(lon, lat); ax.annotate(nm_, (X, Y), xytext=(X + dx, Y + dy), fontsize=10.5, ha="center", arrowprops=dict(arrowstyle="-", color=FG, lw=.7), bbox=dict(boxstyle="round,pad=.2", fc=SEA, ec="none"))
fig.text(.03, .965, f"Antarctic finds: {R['regions']['Antarctica']['n']:,} meteorites, no witnessed falls", fontproperties=DISPB, fontsize=16, color=FG, va="top")
fig.savefig(os.path.join(PA, "f_antarctica.png"), dpi=200, facecolor=BG); plt.close(fig)

# header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.43, .1, .57, .8]); outline(ax, fc=SEA, ec="#C9CDD0", lw=.6); world(ax, lw=.2)
find_stacks(ax, found, k=.55, alpha=.55); fall_dots(ax, fell, s=4)
fig.text(.04, .87, "Where", fontproperties=DISP, fontsize=52, color=FG, va="top")
fig.text(.04, .735, "space rocks", fontproperties=DISP, fontsize=52, color=FALL, va="top")
fig.text(.04, .60, "land", fontproperties=DISP, fontsize=52, color=RCOL["Antarctica"], va="top")
fig.text(.04, .43, f"{R['source']['n']:,} meteorites. {R['regions']['Antarctica']['pct']:.0f}% were found\non Antarctic ice and {R['hot']['pct']:.0f}% in hot deserts.\nThe {R['source']['falls']:,} seen to fall follow people.", fontproperties=SERP, fontsize=14.5, color=FG, va="top", linespacing=1.35)
lg = fig.add_axes([.04, .09, .3, .13]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
for i, (lab, c) in enumerate((("witnessed fall", FALL), ("find: Antarctica", RCOL["Antarctica"]), ("find: hot desert", RCOL["Sahara"]))):
    lg.scatter([.03], [.85 - i * .35], s=40, c=c, lw=0); lg.text(.08, .85 - i * .35, lab, fontsize=10, color=MUT, va="center")
fig.text(.04, .025, "maps.tristanhotham.com/meteorite-falls", fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)
print("figures done", sorted(os.listdir(BL)), sorted(x for x in os.listdir(PA) if x.endswith(".png")))
