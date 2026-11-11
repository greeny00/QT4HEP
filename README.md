# QT4HEP — Preparing CMS jet data for quantum circuits

Zeynep Sağlam · Istanbul Technical University, Department of Physics Engineering
Supervisor: Altan Çakır

Working repository for the CERN QT4HEP poster (24 November 2026) and the MSc thesis.
How jet data must be prepared before it is encoded in a quantum circuit, and what goes wrong otherwise:
scale dominance of raw amplitude encoding, sign blindness after centring (and its repair by constant padding),
the angle scale of one-particle-one-qubit (1P1Q) encodings, finite-shot effects, pT-composition effects on the
evaluation, and a small IBM hardware check. All kernels used here are classically computable; no quantum
advantage is claimed.

## Repository structure

| Folder | Contents |
| --- | --- |
| `Data/` | Raw data (not tracked by Git) |
| `src/` | Reusable Python code: data loading and selection, encodings, kernels, figure style |
| `notebooks/` | Analysis notebooks 01–15 (run in order; each one saves its results and figures) |
| `results/` | JSON / NPZ outputs of the notebooks |
| `figures/` | Poster and thesis figures (PDF + PNG) |
| `notes/` | Research log, environment lock file |
| `docs/` | Abstract, poster drafts |
| `references.bib` | Bibliography (BibTeX) |

## Setup

```bash
conda env create -f environment.yml
conda activate qt4hep
```

## Data

CMS Open Data, record 12100 — DOI: 10.7483/OPENDATA.CMS.RY2V.T797.
Three files are used: `_MC_1` (development), `_MC_10` (confirmation, notebooks 10–13), `_MC_8` (third file, notebooks 14–15).

```bash
cd Data
for i in 1 10 8; do
  cernopendata-client download-files --recid 12100 --filter-name JetNtuple_RunIISummer16_13TeV_MC_$i.h5
  mv 12100/JetNtuple_RunIISummer16_13TeV_MC_$i.h5 . && rmdir 12100
done
```

## Metric

The headline metric is the pT-reweighted ROC AUC (gluon jets reweighted to the quark pT spectrum), see notebook 13.
Inclusive AUCs refer to the unweighted sample, which is flat in generator pT-hat.
