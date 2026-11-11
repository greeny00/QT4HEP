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

## 2026-11-11 — Session 5: pT-reweighted evaluation (MC_10) and constant-padding test (MC_8)

Decision: the headline metric is the pT-reweighted AUC (gluon jets reweighted to the quark pT spectrum). Inclusive AUC is reported only as a secondary number.

- pT-binned comparison (nb 13, confirmation file MC_10, 5 seeds, 400 training jets): dev/confirmation shared events 0; 20 jets without QGL value dropped
  - Check: AUC of jet pT itself, inclusive 0.667, reweighted 0.500
  - pT-reweighted AUC: CMS QGL 0.790; amplitude min-max (1000 shots) 0.770 ± 0.005; amplitude raw (exact) 0.766 ± 0.010; amplitude raw (1000 shots) 0.755 ± 0.005 (inclusive 0.688); RBF-SVM 0.755 ± 0.018; angle robust_yj (1000 shots) 0.752 ± 0.008; BDT 0.737 ± 0.014; QG_axis2 alone 0.695
  - Paired bootstrap (test jets only, seed spread not included), reweighted: min-max - RBF +0.015 [0.015, 0.016]; min-max - QGL -0.020; min-max - raw (both 1000 shots) +0.016; min-max - axis2 alone +0.075
  - Correction of Session 4: the ~0.10 inclusive AUC drop of raw amplitude at 1000 shots is mostly a pT-composition effect. Pure shot cost (raw exact -> 1000 shots) is ~0.011 reweighted; raw vs min-max ~0.016. Inclusive AUC can bias a model up (RBF 0.791 -> 0.755) or down (raw amplitude 0.688 -> 0.755)
  - Not yet re-checked with reweighting: the nb 11 statement that exact-tuned models collapse at finite shots. Do not claim it until re-checked
- Constant-padding cause test (nb 14, third untouched file MC_8, 84498 jets, quark fraction 0.373, shared events with dev 0, 10 seeds)
  - Protocol: src/kernels.py (amplitude_kernel_padded) committed in 1b38d66 before the run. The notebook itself was NOT included in that commit; its cell sources were verified (MD5 of all cell sources) to be identical to the version written before the run
  - Check: AUC of jet pT, inclusive 0.667, reweighted 0.501
  - pT-reweighted AUC (mean ± std over seeds): standardised zero-pad 0.622 ± 0.019 (exact) / 0.622 ± 0.016 (1000 shots); standardised c-pad 0.754 ± 0.014 / 0.758 ± 0.012; min-max zero-pad 0.763 ± 0.009 / 0.761 ± 0.013; min-max c-pad 0.758 ± 0.013 / 0.754 ± 0.011; classical RBF-SVM (standardised) 0.749 ± 0.016
  - Paired over seeds (same training subsample): standardised c-pad - zero-pad +0.132 (exact) / +0.136 (1000 shots), positive in 10/10 seeds; min-max zero-pad - RBF +0.015 (exact) / +0.013 (1000 shots), positive in 8/10 seeds; min-max c-pad - zero-pad -0.005 (3/10 seeds positive)
  - Prediction ("padding recovers standardised inputs to the level of min-max / RBF-SVM") confirmed. Min-max inputs are all positive, so they have no sign problem and padding does not help them
  - Kernel off-diagonal variance is lower for c-pad (2.2e-2) than for zero-pad (1.0e-1) although c-pad performs much better: kernel variance alone does not predict performance at 2 qubits
  - Note: the c-padded amplitude kernel equals a normalised degree-2 polynomial kernel, (x.x' + c^2)^2 / ((|x|^2 + c^2)(|x'|^2 + c^2)). It is classically computable; no quantum-advantage claim

### 2026-11-11 — Corrections after the independent review (all numbers re-checked against results/*.json)

Framing decision: the poster is about preparing jet data for quantum circuits (what goes wrong, how to detect it, how to fix it). The classical RBF-SVM is a reference, not a competitor; the comparison is stated as "comparable".

- Uncertainties: the nb 13 paired-bootstrap intervals exclude training-sample (seed) variance, which dominates. Seed-paired reweighted differences, min-max amplitude (1000 shots) - RBF-SVM: MC_10 +0.025, -0.002, +0.003, +0.031, +0.020 (mean +0.015, SE 0.006, 4/5 positive; inclusive +0.003); MC_8 +0.015 / +0.013 (SE 0.003-0.004, 8/10 positive). Do not quote [0.015, 0.016]
- Session 4, 1P1Q "AUC 0.50-0.51 at published f" was obtained with C = 1. Concentration is not the full explanation: for small angles the kernel is to leading order linear in the signed angles f z dEta, f z dPhi, which carry almost no q/g information by symmetry; the invariant variant's linear term (sum z dR) is girth-like. Tested with tuned C in nb 15
- Bal et al. restrict f to [1, 2pi + 1]; their trained f = 7.27 sits at the upper limit, for top-vs-QCD with a VQC
- Grid edges: raw amplitude exact C = 1e6 in 3/5 seeds and 1P1Q original f = 316 in 3/5 seeds (nb 10); the concentration cost (~0.011 reweighted) is a lower bound. Fits stopping at MAX_ITER were not counted before nb 15
- Hardware A: the empty reference circuit was transpiled separately (no fixed initial_layout) and shows more '10' outcomes (31/4000) than any jet circuit (11-18/4000), so it is not the readout floor of the jet circuits. Correct statement: eta/phi probabilities (1e-7 to 2e-3) are below the total gate + readout error (~3e-3 to 1e-2)
- Hardware B: raw amplitude offset (~0.011) exceeds the whole exact range (0.993-1.000); Pearson 0.92, Spearman 0.70, 28 pairs from 8 jets. Min-max: Pearson 0.999, slope 0.95, intercept 0.03
- Hardware C: product states of single-qubit RY rotations, no two-qubit gates; without a barrier the transpiler merges RY(theta) RY(-theta'). C measures readout scaling of the all-zeros outcome with qubit number, not circuit noise
- Sign blindness: for a balanced training subsample standardised on itself the class means are exactly opposite (mu_q = -mu_g). Constant padding restores sign and norm together; nb 15 separates them. k = 8 (grid edge) chosen in 4/10 exact seeds in nb 14
- nb 14: min-max c-pad - zero-pad at 1000 shots is -0.007 (1/10 positive); the notebook was not part of commit 1b38d66 (see Session 5)
- jetQGl conditions on pT, eta, rho; the three-input models do not, so the reweighted gap to jetQGl (-0.020, MC_10 only) is not a like-for-like encoding comparison. The reweighted metric was chosen after seeing MC_10
- All inclusive AUCs refer to the unweighted sample, flat in generator pT-hat (eventWeight not used)
- Hyperparameters in nb 10-14 were tuned on inclusive CV AUC; nb 15 tunes on pT-reweighted CV AUC
- Finite-shot training kernels are not positive semidefinite and are passed to the SVM without projection
- Std convention: nb 10-11 (Session 4) ddof = 0; nb 13-15 ddof = 1
- All kernels used are classically computable in closed form; no quantum-advantage claim anywhere
- Not re-checked: nb 11 "exact-tuned models collapse at finite shots" (inclusive AUC only); do not quote
