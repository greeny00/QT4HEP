# QT4HEP — Quantum Data Encoding for CMS Jets

Zeynep Sağlam · Istanbul Technical University, Department of Physics Engineering
Supervisor: Altan Çakır

Working repository for the CERN QT4HEP poster (24 November 2026) and the MSc thesis.
Comparison of angle and amplitude encoding on reconstructed CMS jets (pT, η, ϕ, m),
the "state collapse" caused by L2 normalization, and physics-driven encoding strategies.

## Repository structure

| Folder | Contents |
| --- | --- |
| `Data/` | Raw data (not tracked by Git) |
| `src/` | Reusable Python code (data loading, encodings, metrics) |
| `notebooks/` | Exploration and figure notebooks |
| `figures/` | Poster and thesis figures |
| `notes/` | Research log, environment lock file |
| `docs/` | Abstract, poster drafts |
| `references.bib` | Bibliography (BibTeX) |

## Setup

```bash
conda env create -f environment.yml
conda activate qt4hep
```

## Data

CMS Open Data, record 12100 — DOI: 10.7483/OPENDATA.CMS.RY2V.T797

```bash
cd Data
cernopendata-client download-files --recid 12100 --filter-name JetNtuple_RunIISummer16_13TeV_MC_1.h5
mv 12100/JetNtuple_RunIISummer16_13TeV_MC_1.h5 . && rmdir 12100
```
