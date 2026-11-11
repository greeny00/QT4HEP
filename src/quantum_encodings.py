"""Quantum data encodings for jet features.

Amplitude encoding of a feature vector x (length N = 2^n):

    |psi(x)> = sum_i x_i / ||x|| |i>

so the Born probability of basis state |i> is p_i = x_i^2 / ||x||^2.
These probabilities are fixed by the data alone, so they can be computed
analytically (no circuit) and used as ground truth for the circuit output.
"""

import numpy as np


def amplitude_probabilities(X):
    """Analytic Born probabilities of amplitude-encoded rows of X.

    Parameters
    ----------
    X : array, shape (n_samples, n_features)

    Returns
    -------
    array, shape (n_samples, n_features), rows sum to 1.
    p[:, 0] is |alpha_00|^2 for the (pT, eta, phi, m) ordering.
    """
    X = np.asarray(X, dtype=np.float64)
    squared = X**2
    return squared / squared.sum(axis=1, keepdims=True)


def pad_to_power_of_two(x):
    """Zero-pad a 1D vector to the next power-of-two length."""
    x = np.asarray(x, dtype=np.float64)
    n_qubits = max(1, int(np.ceil(np.log2(len(x)))))
    padded = np.zeros(2**n_qubits)
    padded[: len(x)] = x
    return padded, n_qubits


def amplitude_encoding_circuit(x):
    """Qiskit circuit that prepares |psi(x)> with StatePreparation.

    StatePreparation (not Initialize) is used because it is a unitary Gate:
    it can be inverted, which the fidelity kernel U(x')^dagger U(x) requires later.
    """
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import StatePreparation

    padded, n_qubits = pad_to_power_of_two(x)
    state = padded / np.linalg.norm(padded)
    qc = QuantumCircuit(n_qubits, name="amplitude")
    qc.append(StatePreparation(state), range(n_qubits))
    return qc


def angle_encoding_circuit(theta):
    """One qubit per feature, RY(theta_i)|0>. Angles are used as given (the kernel experiments pass preprocessed features directly)."""
    from qiskit import QuantumCircuit

    theta = np.asarray(theta, dtype=np.float64)
    qc = QuantumCircuit(len(theta), name="angle")
    for i, angle in enumerate(theta):
        qc.ry(angle, i)
    return qc
