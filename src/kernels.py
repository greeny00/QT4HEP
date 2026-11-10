"""Preprocessing, quantum kernels and kernel diagnostics for the controlled experiment.

Kernels are computed exactly from the encoded state vectors (noiseless statevector
simulation). For these encodings the overlaps have closed forms:

  amplitude:  |psi(x)> = x / ||x||  (zero-padded to 2^n)   ->  K = (x . x')^2 / (||x||^2 ||x'||^2)
  angle:      |psi(x)> = (x)_i RY(x_i)|0>                  ->  K = prod_i cos^2((x_i - x'_i) / 2)

Notebook 05 cross-checks both against Qiskit Statevector overlaps.

Note: amplitude encoding is blind to the overall sign, |psi(-x)> = -|psi(x)> (a global phase),
so after centring (standard / robust_yj) jets on opposite sides of the mean map to the same state.
"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler, PowerTransformer, RobustScaler, StandardScaler

# raw: no preprocessing; standard: zero mean, unit variance; robust_yj: RobustScaler + Yeo-Johnson
# (both centred, so features change sign); minmax: [0, 1] per feature (equal scales, signs kept positive)
PREPROCESSING = ("raw", "standard", "robust_yj", "minmax")


def preprocess(name, X_train, *X_other):
    """Fit a preprocessing on the training set only and apply it to all arrays."""
    if name == "raw":
        out = [np.asarray(X_train, float)] + [np.asarray(X, float) for X in X_other]
    elif name == "standard":
        scaler = StandardScaler().fit(X_train)
        out = [scaler.transform(X_train)] + [scaler.transform(X) for X in X_other]
    elif name == "robust_yj":
        robust = RobustScaler().fit(X_train)
        power = PowerTransformer(method="yeo-johnson", standardize=True).fit(robust.transform(X_train))
        out = [power.transform(robust.transform(X_train))] + [power.transform(robust.transform(X)) for X in X_other]
    elif name == "minmax":
        scaler = MinMaxScaler().fit(X_train)
        out = [scaler.transform(X_train)] + [scaler.transform(X) for X in X_other]
    else:
        raise ValueError(f"unknown preprocessing: {name}")
    return out if X_other else out[0]


def amplitude_states(X):
    """Normalised, zero-padded amplitude-encoded state vectors, shape (n, 2^n_qubits)."""
    X = np.asarray(X, float)
    n_qubits = max(1, int(np.ceil(np.log2(X.shape[1]))))
    padded = np.zeros((X.shape[0], 2**n_qubits))
    padded[:, : X.shape[1]] = X
    return padded / np.linalg.norm(padded, axis=1, keepdims=True)


def amplitude_kernel(A, B):
    return (amplitude_states(A) @ amplitude_states(B).T) ** 2


def angle_kernel(A, B):
    A, B = np.asarray(A, float), np.asarray(B, float)
    diff = A[:, None, :] - B[None, :, :]
    return np.prod(np.cos(diff / 2) ** 2, axis=2)


KERNELS = {"amplitude": amplitude_kernel, "angle": angle_kernel}


def shot_noise(K, shots, rng, symmetric=False):
    """Replace each kernel entry by a finite-shot estimate (binomial, as on hardware).

    On hardware each entry is estimated as the frequency of the all-zero outcome
    of U(x')^dagger U(x), so the estimate is Binomial(shots, K) / shots.
    """
    K_hat = rng.binomial(shots, np.clip(K, 0, 1)) / shots
    if symmetric:
        upper = np.triu(K_hat, 1)
        K_hat = upper + upper.T
        np.fill_diagonal(K_hat, 1.0)
    return K_hat


def concentration(K):
    """Mean and variance of the off-diagonal kernel values (Thanasilp et al. 2024)."""
    off = K[~np.eye(K.shape[0], dtype=bool)]
    return off.mean(), off.var()


def effective_rank(K):
    """exp(Shannon entropy of the normalised eigenvalue spectrum); between 1 and n."""
    eig = np.clip(np.linalg.eigvalsh(K), 0, None)
    p = eig / eig.sum()
    p = p[p > 0]
    return float(np.exp(-np.sum(p * np.log(p))))


def entanglement_entropy_2q(states):
    """Von Neumann entropy (bits) of one qubit for 2-qubit real states, shape (n, 4).

    Qiskit little-endian: index i = 2*q1 + q0, so reshape (2, 2) puts q1 on the rows.
    """
    M = np.asarray(states).reshape(-1, 2, 2)
    s = np.linalg.svd(M, compute_uv=False) ** 2
    s = np.clip(s, 1e-300, 1)
    return -np.sum(s * np.log2(s), axis=1)


# ---------------------------------------------------------------------------
# 1P1Q encoding (Bal et al., PRD 112, 076004): one qubit per jet constituent
#   theta_i = f * z_i * d_eta_i,   phi_i = f * z_i * d_phi_i,   z_i = pT_i / pT_jet
#   |psi_i> = RX(phi_i) RY(theta_i) |0>,   |psi(jet)> = tensor product over constituents
# Missing constituents (padding) have z = 0 and stay in |0>.
# The paper trains f; here f is fixed and scanned (it plays the role of a kernel bandwidth).
# ---------------------------------------------------------------------------

def onep1q_states(z, d_eta, d_phi, f):
    """Single-qubit states, shape (n_jets, n_constituents, 2), complex."""
    theta = f * z * d_eta
    phi = f * z * d_phi
    c, s = np.cos(theta / 2), np.sin(theta / 2)          # RY(theta)|0> = (c, s)
    cp, sp = np.cos(phi / 2), np.sin(phi / 2)            # RX(phi) = [[cp, -i sp], [-i sp, cp]]
    return np.stack([cp * c - 1j * sp * s, -1j * sp * c + cp * s], axis=-1)


def onep1q_kernel(SA, SB, chunk=500):
    """Fidelity kernel of product states: prod_i |<psi_i(a)|psi_i(b)>|^2 (computed in row chunks)."""
    out = np.empty((SA.shape[0], SB.shape[0]))
    for start in range(0, SA.shape[0], chunk):
        overlaps = np.einsum("aik,bik->abi", SA[start:start + chunk].conj(), SB)
        out[start:start + chunk] = np.prod(np.abs(overlaps) ** 2, axis=2)
    return out
