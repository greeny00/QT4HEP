"""Convergence check for notebook 15, part B (sign or norm).

For every training set and encoding, the C chosen by cross-validation in notebook 15 is refitted twice on the
same 400 training jets: with the notebook's iteration cap (MAX_ITER = 200 000) and without any cap (max_iter = -1).
Both are evaluated on the third file (MC_8) with the pT-reweighted AUC. Nothing is re-tuned.

Run from the repository root:  python scripts/check_selected_fits.py
Writes results/selected_fit_check.json and prints a table.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.svm import SVC

sys.path.insert(0, "src")
from jet_data import load_jets, select_quark_gluon, feature_matrix, event_level_split, balanced_subsample, BOOKKEEPING
from kernels import preprocess, amplitude_kernel, amplitude_kernel_padded

SEED, N_PER_CLASS, MAX_ITER = 42, 200, 200_000
QGL_INPUTS = ("QG_mult", "QG_ptD", "QG_axis2")
DEV_PATH = Path("Data/JetNtuple_RunIISummer16_13TeV_MC_1.h5")
EVAL_PATH = Path("Data/JetNtuple_RunIISummer16_13TeV_MC_8.h5")
RESULTS = Path("results")


def load(path):
    jets = select_quark_gluon(load_jets(path=path, features=QGL_INPUTS + ("jetPt",), extra=BOOKKEEPING), require_loose_id=True)
    return {"jets": jets, "y": jets["label"], "X": feature_matrix(jets, features=QGL_INPUTS), "pt": np.asarray(jets["jetPt"], float)}


def pt_weights(y, pt, n_bins=30, lo=30.0):          # identical to notebook 15
    edges = np.logspace(np.log10(lo), np.log10(pt.max() * 1.001), n_bins + 1)
    hq, _ = np.histogram(pt[y == 1], edges, density=True)
    hg, _ = np.histogram(pt[y == 0], edges, density=True)
    b = np.clip(np.digitize(pt, edges) - 1, 0, n_bins - 1)
    return np.where(y == 1, 1.0, np.divide(hq, hg, out=np.zeros_like(hq), where=hg > 0)[b])


def kernels(variant, param, A, E):
    """Training and evaluation kernels exactly as in notebook 15, part B."""
    if variant == "min-max, zero-pad (reference)":
        raise ValueError("handled by the caller (min-max inputs)")
    nA, nE = np.linalg.norm(A, axis=1), np.linalg.norm(E, axis=1)
    med = float(np.median(nA))
    if variant == "zero-pad (sign and norm lost)":
        return amplitude_kernel(A, A), amplitude_kernel(E, A)
    if variant == "c-pad (sign and norm kept)":
        return amplitude_kernel_padded(A, A, param * med), amplitude_kernel_padded(E, A, param * med)
    if variant == "norm kept, sign lost":
        sp = 1.0 / (param * med)
        nk = lambda P, Q, nP, nQ: amplitude_kernel(P, Q) * np.cos(sp * (nP[:, None] - nQ[None, :]) / 2) ** 2
        return nk(A, A, nA, nA), nk(E, A, nE, nA)
    if variant == "sign kept, norm lost":
        UA, UE = A / nA[:, None], E / nE[:, None]
        return amplitude_kernel_padded(UA, UA, param), amplitude_kernel_padded(UE, UA, param)
    raise ValueError(variant)


dev, ev = load(DEV_PATH), load(EVAL_PATH)
train, _ = event_level_split(dev["jets"], test_fraction=0.3, seed=SEED)
w_ev = pt_weights(ev["y"], ev["pt"])
records = json.load(open(RESULTS / "data_prep_diagnostics.json"))["B"]["records"]
variants = ["zero-pad (sign and norm lost)", "norm kept, sign lost", "sign kept, norm lost",
            "c-pad (sign and norm kept)", "min-max, zero-pad (reference)"]

out = []
print(f"{'encoding':32s} {'set':>3s} {'C':>8s}  {'nb15 AUC':>8s}  {'capped: status, AUC':>20s}  {'no cap: status, AUC, s':>24s}")
for s in sorted({r["seed"] for r in records}):
    idx = balanced_subsample(dev["y"], train, N_PER_CLASS, seed=s)
    y_tr = dev["y"][idx]
    A, E = preprocess("standard", dev["X"][idx], ev["X"])
    Am, Em = preprocess("minmax", dev["X"][idx], ev["X"])
    for v in variants:
        best = max([r for r in records if r["variant"] == v and r["seed"] == s], key=lambda r: r["cv_auc_rw"])
        K_tr, K_ev = (amplitude_kernel(Am, Am), amplitude_kernel(Em, Am)) if v.startswith("min-max") else kernels(v, best["param"], A, E)
        row = {"variant": v, "seed": s, "C": best["C"], "param": best["param"], "auc_rw_nb15": best["auc_rw"]}
        for tag, it in (("capped", MAX_ITER), ("uncapped", -1)):
            t0 = time.time()
            svc = SVC(kernel="precomputed", C=best["C"], max_iter=it).fit(K_tr, y_tr)
            row[f"{tag}_status"] = int(svc.fit_status_)
            row[f"{tag}_auc_rw"] = float(roc_auc_score(ev["y"], svc.decision_function(K_ev), sample_weight=w_ev))
            row[f"{tag}_seconds"] = round(time.time() - t0, 1)
        out.append(row)
        print(f"{v:32s} {s:3d} {best['C']:8.0e}  {best['auc_rw']:8.3f}  {row['capped_status']:>8d}, {row['capped_auc_rw']:.3f}"
              f"      {row['uncapped_status']:>6d}, {row['uncapped_auc_rw']:.3f}, {row['uncapped_seconds']:6.1f}", flush=True)

json.dump(out, open(RESULTS / "selected_fit_check.json", "w"), indent=2)
print("\nsaved results/selected_fit_check.json\n")
for v in variants:
    a = np.array([r["uncapped_auc_rw"] for r in out if r["variant"] == v])
    capped = sum(r["capped_status"] != 0 for r in out if r["variant"] == v)
    print(f"{v:32s} uncapped mean {a.mean():.3f} ± {a.std(ddof=1):.3f} (selected fits stopped at the cap in nb15: {capped}/{len(a)})")
z = np.array([r["uncapped_auc_rw"] for r in out if r["variant"] == variants[0]])
for v in variants[1:4]:
    d = np.array([r["uncapped_auc_rw"] for r in out if r["variant"] == v]) - z
    print(f"paired {v} - zero-pad: {d.mean():+.3f} (SE {d.std(ddof=1) / np.sqrt(len(d)):.3f}), positive in {np.sum(d > 0)}/{len(d)}")
