"""Poster figures for QT4HEP 2026 (A0 portrait), drawn at their printed size.

Run from the repository root:  python scripts/make_poster_figures.py
Reads results/*.json written by notebooks 12-15; writes figures/poster/*.png (300 dpi) and *.pdf.
All text is >= 18 pt at printed size (conference minimum).
"""

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

RESULTS = Path("results")
OUT = Path("figures/poster")
OUT.mkdir(parents=True, exist_ok=True)

# Chart colours: the validated palette of src/figure_style.py
BLUE, ORANGE, GREEN, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
INK, MUTED, GRIDC = "#1a1a1a", "#4a4a4a", "#d9dce1"
PANEL = "#f3f5f8"          # same as the poster box fill, so figures sit flush on the box
W = 9.2                    # printed width in inches (one poster column minus padding)

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 22, "axes.labelsize": 22, "xtick.labelsize": 20, "ytick.labelsize": 20, "legend.fontsize": 19,
    "figure.facecolor": PANEL, "axes.facecolor": PANEL, "savefig.facecolor": PANEL,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True,
    "grid.color": GRIDC, "grid.linewidth": 1.0, "lines.linewidth": 3.2, "lines.markersize": 10,
    "legend.frameon": False, "savefig.dpi": 300, "axes.linewidth": 1.4,
    "xtick.major.width": 1.4, "ytick.major.width": 1.4, "xtick.major.size": 7, "ytick.major.size": 7,
})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}")
    plt.close(fig)
    print(f"saved {OUT / name}.png/.pdf")


# ---------------------------------------------------------------- 1. scale (Phase 1)
# Mean Born probabilities of raw (pT, eta, phi, m) amplitude encoding, 13,912 q/g jets of MC_1
# (printed output of notebook 02, section 5).
gev = [0.9829, 1.21e-4, 2.42e-4, 0.0167]
tev = [0.0862, 0.3276, 0.5853, 0.0009]
fig, ax = plt.subplots(figsize=(W, 4.4))
pos = np.arange(4)
for off, vals, col, lab in ((-0.2, gev, BLUE, r"$p_T$, $m$ in GeV"), (0.2, tev, ORANGE, r"$p_T$, $m$ in TeV")):
    bars = ax.bar(pos + off, vals, 0.38, color=col, label=lab)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.35, f"{v:.2f}" if v >= 0.01 else f"{v:.0e}".replace("e-0", "e-"),
                ha="center", va="bottom", fontsize=18, color=INK)
ax.set_yscale("log"); ax.set_ylim(5e-5, 60); ax.set_yticks([1e-4, 1e-3, 1e-2, 1e-1, 1], ["0.0001", "0.001", "0.01", "0.1", "1"]); ax.minorticks_off()
ax.set_xticks(pos, [r"$|00\rangle$  $p_T$", r"$|01\rangle$  $\eta$", r"$|10\rangle$  $\phi$", r"$|11\rangle$  $m$"])
ax.set_ylabel("mean probability")
ax.grid(axis="x", visible=False)
ax.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03))
fig.tight_layout()
save(fig, "p1_scale")

# ---------------------------------------------------------------- 2. sign or norm (nb 15, part B)
# The C chosen by CV in notebook 15 is refitted without an iteration cap (scripts/check_selected_fits.py);
# the poster shows these converged fits (one capped zero-pad fit in notebook 15 had not converged).
d15 = json.load(open(RESULTS / "data_prep_diagnostics.json"))
check = json.load(open(RESULTS / "selected_fit_check.json"))
B = {v: {"auc_rw": [r["uncapped_auc_rw"] for r in sorted(check, key=lambda r: r["seed"]) if r["variant"] == v]}
     for v in {r["variant"] for r in check}}
rows = [("zero-pad (sign + norm lost)", "zero-pad (sign and norm lost)", BLUE),
        ("norm kept, sign lost", "norm kept, sign lost", BLUE),
        ("sign kept, norm lost", "sign kept, norm lost", GREEN),
        ("constant pad (both kept)", "c-pad (sign and norm kept)", GREEN),
        ("min-max inputs (reference)", "min-max, zero-pad (reference)", GREY)]
fig_s, axs = plt.subplots(figsize=(2.9, 3.2))          # schematic, placed at this size
fig_s.subplots_adjust(0, 0, 1, 1)
axs.set_xlim(-1.25, 1.25); axs.set_ylim(-1.3, 1.3); axs.set_aspect("equal"); axs.axis("off")
axs.add_patch(plt.Circle((0, 0), 1, fill=False, color=MUTED, lw=1.6, ls=(0, (4, 3))))
ang = np.deg2rad(35); u = np.array([np.cos(ang), np.sin(ang)])
axs.annotate("", xy=u * 0.98, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=3.5, mutation_scale=28))
axs.annotate("", xy=-u * 0.98, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=3.5, mutation_scale=28))
axs.text(u[0] * 0.55 - 0.05, u[1] * 0.55 + 0.22, r"$\mu_q$", color=BLUE, fontsize=26, ha="right")
axs.text(-u[0] * 0.55 + 0.05, -u[1] * 0.55 - 0.22, r"$\mu_g=-\mu_q$", color=ORANGE, fontsize=24, ha="left", va="top")
axs.text(0, -1.27, "same state", ha="center", va="top", fontsize=22, color=INK)
axs.set_ylim(-1.55, 1.3)
save(fig_s, "p2a_sign_schematic")
fig, ax = plt.subplots(figsize=(W, 5.5))
y = np.arange(len(rows))[::-1]
for yy, (lab, key, col) in zip(y, rows):
    a = np.array(B[key]["auc_rw"])
    ax.errorbar(a.mean(), yy, xerr=a.std(ddof=1), fmt="o", color=col, markersize=13, capsize=5, elinewidth=2.5,
                markeredgecolor="white", markeredgewidth=1.5)
    ax.text(0.83, yy, f"{a.mean():.2f}", va="center", ha="right", fontsize=20, color=INK)
ax.set_yticks(y, [r[0] for r in rows], fontsize=20)
ax.set_xlim(0.5, 0.835); ax.set_xticks([0.5, 0.6, 0.7, 0.8])
ax.set_xlabel(r"$p_T$-reweighted AUC")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "p2_sign")

# ---------------------------------------------------------------- 3. angle scale (nb 15, part A)
A = d15["A"]["records"]; refs = d15["A"]["references"]
fs = sorted({r["f"] for r in A})
def curve(variant, budget):
    return np.array([np.mean([r["auc_rw"] for r in A if r["variant"] == variant and r["budget"] == budget and r["f"] == f]) for f in fs])
fig, ax = plt.subplots(figsize=(W, 7.0))
ax.plot(fs, curve("original", 1000), "o-", color=BLUE, label="1P1Q, 1000 shots")
ax.plot(fs, curve("original", "exact"), "o--", color=BLUE, alpha=0.55, label="1P1Q, exact kernel")
ax.plot(fs, curve("invariant", 1000), "s-", color=GREEN, label="invariant 1P1Q, 1000 shots")
ax.plot(fs, curve("invariant", "exact"), "s--", color=GREEN, alpha=0.55, label="invariant 1P1Q, exact kernel")
ax.axhline(np.mean(refs["sum z dR (no training)"]), color=GREY, ls=":", lw=2.5)
ax.text(80, 0.618, r"untrained $\sum z\,\Delta R$", color=GREY, fontsize=19)
ax.axvline(7.27, color=GREY, ls="--", lw=1.8)
ax.text(6.8, 0.509, "f of Bal et al.", color=GREY, fontsize=18, ha="right")
ax.set_xscale("log"); ax.set_xlabel("scale factor f"); ax.set_ylabel(r"$p_T$-reweighted AUC")
ax.set_xticks([1, 10, 100, 1000], ["1", "10", "100", "1000"])
ax.set_ylim(0.49, 0.64)
a_per_f = np.median([r["median_angle"] / r["f"] for r in A if r["variant"] == "original"])
top = ax.secondary_xaxis("top", functions=(lambda f: f * a_per_f, lambda a: a / a_per_f))
top.set_xlabel(r"median $|\theta|$ (rad), original 1P1Q", fontsize=20, color=MUTED)
top.set_xticks([0.01, 0.1, 1], ["0.01", "0.1", "1"])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=18, columnspacing=1.0, handlelength=2.2)
fig.tight_layout()
save(fig, "p3_angle")

# ---------------------------------------------------------------- 4. evaluation: inclusive vs pT-reweighted (nb 13, MC_10)
t = json.load(open(RESULTS / "pt_binned_comparison.json"))["table"]
order = [(r"CMS QGL ($p_T$, $\eta$, $\rho$ bins)", "CMS QGL"), ("amplitude, min-max", "amplitude, min-max (1000 shots)"),
         ("amplitude, raw", "amplitude, raw (1000 shots)"), ("RBF-SVM (classical)", "RBF-SVM (classical)"),
         ("angle, robust + YJ", "angle, robust + YJ (1000 shots)"), ("BDT (classical)", "BDT (classical)"),
         ("QG_axis2 alone", "QG_axis2 alone (no training)")]
vals = [(lab, np.mean(t[k]["inclusive"]), np.mean(t[k]["reweighted"])) for lab, k in order]
vals.append((r"jet $p_T$ alone", 0.667, 0.500))          # notebook 13 sanity check on the same file
fig, ax = plt.subplots(figsize=(W, 5.4))
y = np.arange(len(vals))[::-1]
for yy, (lab, inc, rw) in zip(y, vals):
    ax.annotate("", xy=(rw, yy), xytext=(inc, yy), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=2.2, mutation_scale=20,
                                                                 shrinkA=9, shrinkB=9))
    ax.plot(inc, yy, "o", mfc="white", mec=GREY, mew=2.5, markersize=13)
    ax.plot(rw, yy, "o", color=BLUE, markersize=13, mec="white", mew=1.5)
ax.set_yticks(y, [v[0] for v in vals], fontsize=19)
ax.set_xlim(0.48, 0.82); ax.set_xlabel("AUC")
ax.grid(axis="y", visible=False)
ax.plot([], [], "o", mfc="white", mec=GREY, mew=2.5, markersize=13, label=r"inclusive (flat $\hat{p}_T$ sample)")
ax.plot([], [], "o", color=BLUE, markersize=13, label=r"$p_T$-reweighted")
ax.legend(loc="lower center", bbox_to_anchor=(0.35, 1.0), ncol=2, fontsize=18, columnspacing=1.0, handletextpad=0.3)
fig.tight_layout()
save(fig, "p4_evaluation")

# ---------------------------------------------------------------- 5. hardware (nb 12, saved IBM counts)
hw = json.load(open(RESULTS / "ibm_results.json")); shots = hw["run"]["shots"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 4.5), gridspec_kw={"wspace": 0.42})
for ax_, prep, col, lim in ((a1, "minmax", GREEN, (0.15, 1.02)), (a2, "raw", BLUE, (0.975, 1.001))):
    sel = [(m, c) for m, c in zip(hw["meta"], hw["counts"]) if m["exp"] == "B" and m["prep"] == prep]
    ex = np.array([m["exact"] for m, _ in sel]); me = np.array([c.get("00", 0) / shots for _, c in sel])
    ax_.plot(lim, lim, color=GREY, lw=1.8, ls="--")
    ax_.plot(ex, me, "o", color=col, markersize=10, mec="white", mew=1.2)
    ax_.set_xlim(lim); ax_.set_ylim(lim); ax_.set_aspect("equal")
    ax_.set_xlabel("exact kernel")
    ax_.set_title("min-max amplitude" if prep == "minmax" else "raw amplitude (zoom)", fontsize=20, loc="left")
a2.set_xticks([0.98, 0.99, 1.0]); a2.set_yticks([0.98, 0.99, 1.0])
a1.set_ylabel("measured (hardware)")
fig.subplots_adjust(left=0.13, right=0.98, bottom=0.2, top=0.9)
save(fig, "p5_hardware")
