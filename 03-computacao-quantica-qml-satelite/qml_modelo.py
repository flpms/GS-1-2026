"""
qml_modelo.py — Modelos de Quantum Machine Learning (Qiskit).

Implementa dois paradigmas de QML para classificação binária:

  1. QSVC (Quantum Support Vector Classifier): usa um kernel quântico
     (FidelityQuantumKernel) construído sobre um mapa de características ZZFeatureMap.
     O kernel mede a similaridade entre estados quânticos preparados a partir dos
     dados — é o análogo quântico do "kernel trick" do SVM clássico.

  2. VQC (Variational Quantum Classifier): rede neural quântica variacional, com um
     mapa de características (ZZFeatureMap) seguido de um ansatz parametrizado
     (RealAmplitudes), otimizado classicamente (COBYLA).

Ambos são executados no simulador Aer (StatevectorSampler), pois hardware quântico
real (NISQ) tem poucos qubits, ruído e filas de execução. O número de qubits é igual
ao número de atributos (após PCA).
"""

import time
import numpy as np

from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit.primitives import StatevectorSampler
from qiskit_machine_learning.state_fidelities import ComputeUncompute
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC, VQC
from qiskit_machine_learning.optimizers import COBYLA
from sklearn.metrics import accuracy_score, f1_score


def _profundidade(circuito) -> int:
    try:
        return circuito.decompose().depth()
    except Exception:
        return circuito.depth()


def rodar_qsvc(X_tr, y_tr, X_te, y_te, n_qubits: int, reps: int = 2) -> dict:
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=reps)
    fidelity = ComputeUncompute(sampler=StatevectorSampler())
    kernel = FidelityQuantumKernel(feature_map=feature_map, fidelity=fidelity)

    modelo = QSVC(quantum_kernel=kernel)
    t0 = time.perf_counter()
    modelo.fit(X_tr, y_tr)
    t_treino = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = modelo.predict(X_te)
    t_infer = time.perf_counter() - t1

    return {
        "modelo": "QSVC (kernel quântico)",
        "tipo": "quântico",
        "acuracia": accuracy_score(y_te, y_pred),
        "f1": f1_score(y_te, y_pred, zero_division=0),
        "t_treino_s": t_treino,
        "t_inferencia_s": t_infer,
        "n_qubits": n_qubits,
        "profundidade_circuito": _profundidade(feature_map),
    }


def rodar_vqc(X_tr, y_tr, X_te, y_te, n_qubits: int,
              reps_fm: int = 2, reps_ansatz: int = 2, maxiter: int = 60) -> dict:
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=reps_fm)
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=reps_ansatz)

    modelo = VQC(
        feature_map=feature_map,
        ansatz=ansatz,
        optimizer=COBYLA(maxiter=maxiter),
        sampler=StatevectorSampler(),
    )
    t0 = time.perf_counter()
    modelo.fit(X_tr, y_tr)
    t_treino = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = modelo.predict(X_te)
    t_infer = time.perf_counter() - t1

    prof = _profundidade(feature_map) + _profundidade(ansatz)
    return {
        "modelo": "VQC (variacional)",
        "tipo": "quântico",
        "acuracia": accuracy_score(y_te, y_pred),
        "f1": f1_score(y_te, y_pred, zero_division=0),
        "t_treino_s": t_treino,
        "t_inferencia_s": t_infer,
        "n_qubits": n_qubits,
        "profundidade_circuito": prof,
    }
