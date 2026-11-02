"""Data loading for the CMS Open Data JetNTuple sample (record 12100).

The HDF5 file stores one flat dataset per variable, one row per jet.
Per-jet variables are numeric arrays; PF-candidate variables (PF_pT, PF_dEta, ...)
are variable-length arrays (dtype=object), one array per jet.

Dataset: Kallonen (2019), DOI 10.7483/OPENDATA.CMS.RY2V.T797
Jets: anti-kt R=0.4, CHS, pT > 30 GeV, |eta| < 2.5 (selection applied upstream).
Units: pT and mass in GeV, phi in radians, eta dimensionless.
"""

from pathlib import Path

import h5py
import numpy as np

DEFAULT_PATH = Path("Data/JetNtuple_RunIISummer16_13TeV_MC_1.h5")

# Order matters for amplitude encoding: index i -> basis state |i> (Qiskit little-endian).
# 0 -> |00> pT, 1 -> |01> eta, 2 -> |10> phi, 3 -> |11> mass
JET_FEATURES = ("jetPt", "jetEta", "jetPhi", "jetMass")
FEATURE_LABELS = {
    "jetPt": r"$p_T$ [GeV]",
    "jetEta": r"$\eta$",
    "jetPhi": r"$\phi$ [rad]",
    "jetMass": r"$m$ [GeV]",
}

# Columns needed for labels, quality and the event-level split
BOOKKEEPING = ("run", "lumi", "event", "isPhysUDS", "isPhysG", "isPhysOther", "jetLooseID")


def load_jets(path=DEFAULT_PATH, features=JET_FEATURES, extra=BOOKKEEPING):
    """Read per-jet columns into a dict of numpy arrays."""
    with h5py.File(path, "r") as f:
        return {key: f[key][:] for key in (*features, *extra)}


def select_quark_gluon(data, require_loose_id=True):
    """Keep light-quark (u, d, s) and gluon jets ('physics' flavour definition).

    Adds data["label"]: 1 = quark (isPhysUDS), 0 = gluon (isPhysG).
    b, c and undefined jets (isPhysOther) are dropped.
    """
    mask = (data["isPhysUDS"] == 1) | (data["isPhysG"] == 1)
    if require_loose_id:
        mask &= data["jetLooseID"] == 1
    selected = {key: values[mask] for key, values in data.items()}
    selected["label"] = selected["isPhysUDS"].astype(np.int8)
    return selected


def feature_matrix(data, features=JET_FEATURES, dtype=np.float64):
    """Stack features into an (n_jets, n_features) array in float64.

    The file stores float32; float64 avoids precision artefacts when
    comparing against circuit probabilities at the 1e-7 level.
    """
    return np.stack([np.asarray(data[key], dtype=dtype) for key in features], axis=1)


def event_level_split(data, test_fraction=0.3, seed=42):
    """Train/test masks that keep all jets of one collision event on the same side.

    Jets from the same event are correlated; splitting jet-by-jet would leak
    information from the test set into the training set.
    Events are identified by (run, lumi, event).
    """
    keys = np.stack(
        [np.asarray(data[k], dtype=np.uint64) for k in ("run", "lumi", "event")], axis=1
    )
    _, event_index = np.unique(keys, axis=0, return_inverse=True)
    event_index = event_index.ravel()
    n_events = event_index.max() + 1

    rng = np.random.default_rng(seed)
    test_events = rng.choice(n_events, size=int(round(test_fraction * n_events)), replace=False)
    is_test = np.isin(event_index, test_events)
    return ~is_test, is_test
