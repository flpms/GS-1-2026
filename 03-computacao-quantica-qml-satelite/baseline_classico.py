"""
baseline_classico.py — Modelos clássicos de referência (baseline).

Treina e avalia classificadores clássicos equivalentes ao QML para comparação justa:
SVM com kernel RBF (análogo clássico do kernel quântico) e Random Forest.
Retorna métricas de precisão, F1 e tempos de treino/inferência.
"""

import time
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score


def _avaliar(modelo, X_tr, y_tr, X_te, y_te, nome: str) -> dict:
    t0 = time.perf_counter()
    modelo.fit(X_tr, y_tr)
    t_treino = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = modelo.predict(X_te)
    t_infer = time.perf_counter() - t1

    return {
        "modelo": nome,
        "tipo": "clássico",
        "acuracia": accuracy_score(y_te, y_pred),
        "f1": f1_score(y_te, y_pred, zero_division=0),
        "t_treino_s": t_treino,
        "t_inferencia_s": t_infer,
        "n_qubits": 0,
        "profundidade_circuito": 0,
    }


def rodar_baselines(X_tr, y_tr, X_te, y_te) -> list[dict]:
    resultados = []
    resultados.append(_avaliar(
        SVC(kernel="rbf", C=1.0, gamma="scale"), X_tr, y_tr, X_te, y_te, "SVM (RBF)"))
    resultados.append(_avaliar(
        RandomForestClassifier(n_estimators=200, random_state=42),
        X_tr, y_tr, X_te, y_te, "Random Forest"))
    return resultados
