"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the fireball palette, and Natural Earth outlines in Equal Earth and south polar projections."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#636A72", "axes.labelcolor": "#1D2128",
                     "xtick.color": "#636A72", "ytick.color": "#636A72"})
BG, FG, MUT, LAND, RULE, SEA = "#F6F4EF", "#1D2128", "#636A72", "#E2DED3", "#DDD8CC", "#EEF1F2"
FALL, LESS = "#D4481A", "#9C8460"
RCOL = dict(REGIONS); GCOL = dict(GROUPS)

EE = Transformer.from_crs(4326, 8857, always_xy=True)
SP = Transformer.from_crs(4326, 3031, always_xy=True)
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    for ring in rings(f["geometry"]):
        x, y = EE.transform(np.clip(ring[:, 0], -179.9, 179.9), np.clip(ring[:, 1], -89.5, 89.5))
        SHAPES.append((f["properties"]["iso"], np.column_stack([x, y]), ring))
WORLD_EXT = (-17.0e6, 17.0e6, -8.75e6, 8.7e6)


def world(ax, colour_of=lambda iso: None, lw=.3, ext=WORLD_EXT, ec="#FFFFFF", land=LAND, z=1):
    for iso, p, _ in SHAPES:
        c = colour_of(iso)
        ax.add_patch(MPoly(p, closed=True, fc=land if c is None else c, ec=ec, lw=lw, zorder=z))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")


def outline(ax, fc=None, lw=.8, ec=MUT, z=0):
    """Equal Earth globe outline."""
    lat = np.linspace(-90, 90, 181)
    xl, yl = EE.transform(np.full_like(lat, -180), lat); xr, yr = EE.transform(np.full_like(lat, 180), lat[::-1])
    ax.add_patch(MPoly(np.column_stack([np.r_[xl, xr], np.r_[yl, yr]]), closed=True, fc=fc or "none", ec=ec, lw=lw, zorder=z))


def antarctica(ax, land=LAND, ec="#FFFFFF", lw=.4, lat_min=-60):
    """South polar stereographic map of everything south of lat_min."""
    for iso, _, ring in SHAPES:
        if ring[:, 1].max() > lat_min + 3:
            continue
        x, y = SP.transform(ring[:, 0], np.maximum(ring[:, 1], -89.9))
        ax.add_patch(MPoly(np.column_stack([x, y]), closed=True, fc=land, ec=land, lw=lw, zorder=1))
    r = SP.transform(0, lat_min)[1]
    ax.set_xlim(-abs(r), abs(r)); ax.set_ylim(-abs(r), abs(r)); ax.set_aspect("equal"); ax.axis("off")
    return abs(r)


def proj(lon, lat):
    return EE.transform(np.asarray(lon), np.asarray(lat))


def points():
    P = jload(f"{DATA}/points.json")["rows"]
    return np.array([[p[0], p[1], p[2], p[3], p[4], p[5], p[6]] for p in P], dtype=float), P


def stacks(A, cell=0.5):
    """Aggregate rows of A (lat, lon, ...) into cells; returns lat, lon (mean), count."""
    k = np.floor(A[:, 0] / cell).astype(int) * 100000 + np.floor(A[:, 1] / cell).astype(int)
    u, inv, n = np.unique(k, return_inverse=True, return_counts=True)
    la = np.bincount(inv, A[:, 0]) / n; lo = np.bincount(inv, A[:, 1]) / n
    return la, lo, n


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def ant_inset(fig, rect, rows, k=1.0, title=None, ring=True):
    """Polar inset of Antarctic finds (rows with region 0), circles sized by finds per half-degree square."""
    ax = fig.add_axes(rect)
    r = abs(SP.transform(0, -60)[1])
    ax.add_patch(plt.Circle((0, 0), r, fc=SEA, ec="#C9CDD0" if ring else "none", lw=.8, zorder=0))
    antarctica(ax, lat_min=-60)
    s = rows[rows[:, 6] == 0]
    la, lo, n = stacks(s, .5); x, y = SP.transform(lo, la); o = np.argsort(-n)
    ax.scatter(x[o], y[o], s=k * (2 + 3 * np.sqrt(n[o])), c=RCOL["Antarctica"], alpha=.6, lw=.3, edgecolor="#fff", zorder=3)
    if title: ax.set_title(title, fontsize=10, color=FG, pad=3)
    return ax
