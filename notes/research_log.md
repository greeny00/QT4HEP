# Research Log

Each session: date, commit, versions/seed, what worked, where I got stuck, open questions, next step.

---

## 2026-10-30 — Session 0: Environment setup

- Environment: conda (Miniforge), `qt4hep`, Python 3.12, Qiskit 2.6.1, qiskit-machine-learning 0.9.1 (full list: `requirements-lock.txt`)
- Data: CMS Open Data record 12100, `JetNtuple_RunIISummer16_13TeV_MC_1.h5` (175,842,712 bytes), stored in `Data/`
- Created folder structure, `.gitignore`, `environment.yml`, VS Code settings
- Repository published to GitHub (private): greeny00/QT4HEP
- Open questions: internal structure of the file (HDF5 keys, layout of the PF candidate arrays) not yet inspected
- Next step: run `notebooks/01_data_inspection.ipynb`

## 2026-10-30 — Session 1: Data inspection

- `notebooks/01_data_inspection.ipynb` run: 28,614 jets; one flat HDF5 dataset per variable, no attributes
- Per-jet variables are numeric (float32 / int32; `event` uint64); PF-candidate variables (`PF_pT`, `PF_dEta`, `PF_dPhi`, ...) are variable-length arrays (dtype=object), one per jet
- Gen-level PF arrays have `genJetPF_dR` / `genJetPF_dTheta` but no dEta / dPhi
- Added `src/jet_data.py` (loading, quark/gluon selection, event-level split), `src/quantum_encodings.py`, `src/figure_style.py`
- Next step: run `notebooks/02_amplitude_encoding_collapse.ipynb` and paste its summary lines below

## 2026-11-02 — Session 2: Amplitude Encoding Collapse

- Selection: 13912 quark+gluon jets (quark fraction 0.381); split train 9729 / test 4183, seed 42
- |a00|^2 median 0.9861; fraction > 0.99: 0.354
- Median share of m^2 in residual: 0.996; median m/pT 0.118
- Mean P(|00>) GeV 0.983 vs TeV 0.086
- Circuit check: max |SV - analytic| 1.1e-16; max |Sampler - analytic| 7.6e-04 (10000 shots)
- Qiskit 2.6.1
