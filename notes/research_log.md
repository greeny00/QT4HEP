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

## 2026-11-03 — Session 3: Feature Selection

- Single-feature separation AUC (train): jetQGl 0.791, QG_axis2 0.786, QG_ptD 0.766, jetGirth 0.763, jetPt 0.662, QG_mult 0.627, jetMult 0.620, jetMass 0.563, jetPhi 0.503, jetEta 0.502
- Chosen features: QG_mult, QG_ptD, QG_axis2, jetGirth
- Raw amplitude encoding on chosen features: median dominant probability 0.9997; fraction > 0.9: 1.000
- Dominant state is QG_mult in 1.000 of jets

## 2026-11-10 — Session 4: Baselines, kernel experiments, 1P1Q, final evaluation, IBM hardware

Decisions: inputs = 3 CMS QGL variables (QG_mult, QG_ptD, QG_axis2); abstract's 3.64e-6 dropped; pT never a model input; min-max added to the preprocessing grid; LP2B kept as future work.

- Baselines (nb 04, dev test 4183 jets): CMS QGL 0.790; BDT full 0.787; RBF-SVM full 0.772; 400-jet subsamples: RBF-SVM 0.782 ± 0.004, BDT 0.746 ± 0.007. pT bins (30-100 / 100-300 / >300): QGL 0.740 / 0.778 / 0.808
- Kernel experiment (nb 05, C = 1, exploratory): amplitude raw 0.699 (K var 1.4e-5, eff. rank 1.01); amplitude standardised 0.614 and robust_yj 0.576 (not concentrated: sign blindness); amplitude min-max 0.800; angle robust_yj 0.786; angle min-max 0.794. Qiskit cross-check 1e-15
- Shot budget (nb 06): N* formula does not predict the breakdown point; most concentrated kernel loses ~2x more AUC at 10 shots
- 1P1Q (nb 07): at published f (1-7.27) median angle 0.002-0.017 rad, kernel concentrated, AUC 0.50-0.51; f = 50 (beyond paper): 0.660 (N = 10)
- 1P1Q controls (nb 08): classical on (z, d_eta, d_phi) 0.760; on 1P1Q angles 0.690; rotation-invariant variant (ours, theta = f z dR) 0.692 at f = 7.27, 0.712 at f = 50
- Learned f by CV (nb 09): original f ~187, AUC 0.686 ± 0.002; invariant f ~39, AUC 0.711 ± 0.005
- Final evaluation (nb 10): CV-tuned C (and f), 5 seeds, confirmation file JetNtuple_RunIISummer16_13TeV_MC_10.h5 (~70k jets), dev and confirmation agree within 0.006. Exact: amplitude raw 0.784, standardised 0.617, min-max 0.793; angle robust_yj 0.789, min-max 0.793; 1P1Q original 0.689, invariant 0.703; RBF-SVM 0.791, BDT 0.777, CMS QGL 0.787. 1P1Q inclusive AUC ~0.05 above its pT-bin AUCs (pT composition); invariant > original in every pT bin
- Shot-aware tuning (nb 11, CV on finite-shot kernels): 1000 / 10000 shots: amplitude raw 0.688 / 0.690 (vs 0.784 exact); standardised 0.601 / 0.617; min-max 0.794 / 0.794; angle robust_yj 0.789 / 0.788; angle min-max 0.789 / 0.788; 1P1Q original 0.688 / 0.689; invariant 0.698 / 0.697. Exact-tuned models evaluated at 1000 shots collapse (invariant 1P1Q 0.592, angle min-max 0.756)
- IBM hardware (nb 12): ibm_marrakesh, job dbpg1o8qtr0c738ebupg, 4000 shots, 2026-11-10, no mitigation
  - A: readout floor P(01) 0.0013, P(10) 0.0077; eta/phi amplitudes (1e-7 to 2e-3) measured as 3e-3 to 1e-2: buried in noise; mass amplitude (0.009-0.04) reproduced within ~0.005
  - B: raw amplitude: exact K range 0.993-1.000 (width 0.007), hardware 0.980-0.992 (offset ~0.011), r = 0.92; min-max: exact 0.20-0.99, hardware 0.24-0.98, r = 0.999, slope 0.95
  - C: rotation-invariant 1P1Q self-overlap (ideal 1) vs qubits: 2q 0.989, 4q 0.976, 6q 0.958, 8q 0.949, 10q 0.929; measured/exact for different jets 1.00 at 2q to 0.92 at 10q
