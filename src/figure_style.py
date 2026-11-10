"""Shared figure style for poster and thesis figures."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

FIG_DIR = Path("figures")

# Validated categorical palette (light surface), fixed order
COLORS = {
    "quark": "#2a78d6",   # slot 1, blue
    "gluon": "#eb6834",   # slot 2, orange
    "single": "#2a78d6",  # single-series default
    "series1": "#2a78d6",  # generic slot 1
    "series2": "#eb6834",  # generic slot 2
    "series3": "#1baf7a",  # generic slot 3 (aqua)
    "reference": "#52514e",  # secondary ink for reference lines
}
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"


def set_style():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": TEXT_SECONDARY,
        "axes.labelcolor": TEXT_PRIMARY,
        "axes.titlecolor": TEXT_PRIMARY,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": TEXT_SECONDARY,
        "ytick.color": TEXT_SECONDARY,
        "legend.frameon": False,
        "font.size": 10,
        "lines.linewidth": 2,
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def save(fig, name):
    """Save a figure as vector PDF (poster) and PNG (preview) in figures/."""
    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"{name}.{ext}")
    print(f"saved figures/{name}.pdf and .png")
