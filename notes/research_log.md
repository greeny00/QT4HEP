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
