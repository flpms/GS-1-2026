"""
experimento_robustez.py — Robustez estatística (multi-semente).

Motivação: o experimento original usa um único split/semente e um teste de
apenas 36 amostras, o que torna frágil qualquer comparação entre modelos. Aqui
repetimos o protocolo para N_SEEDS sementes diferentes (amostragem do
subconjunto + split treino/teste) e reportamos média ± desvio-padrão de
acurácia, precisão, recall e F1 para cada modelo. Isso permite afirmar se a
vantagem do QSVC é real ou está dentro da variância.

Modelos: SVM (RBF), Random Forest, QSVC (kernel quântico), VQC (variacional).
Todos no MESMO subconjunto balanceado reduzido (comparação justa), simulador
ideal (StatevectorSampler).

Saídas:
  resultados/robustez.csv   — uma linha por (modelo, seed)
  resultados/robustez_resumo.csv — média ± desvio por modelo
  resultados/robustez.png   — barras com barra de erro (acurácia e F1)

Uso: python experimento_robustez.py
"""

import os, sys, json, time, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score)

from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit.primitives import StatevectorSampler
from qiskit_machine_learning.state_fidelities import ComputeUncompute
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC, VQC
from qiskit_machine_learning.optimizers import COBYLA

from comum import preparar_dados, subconjunto_balanceado, split_treino_teste, preprocessar_split

warnings.filterwarnings("ignore")

N_QUBITS = 4
N_AMOSTRAS = 120          # mesmo tamanho do experimento original (84 treino / 36 teste)
TEST_SIZE = 0.3
SEEDS = [0, 1, 2, 7, 13, 21, 42, 99]   # 8 sementes
DIR = "resultados"


def _metricas(nome, tipo, y_te, y_pred, t_treino):
    return {
        "modelo": nome, "tipo": tipo,
        "acuracia": accuracy_score(y_te, y_pred),
        "precisao": precision_score(y_te, y_pred, zero_division=0),
        "recall":   recall_score(y_te, y_pred, zero_division=0),
        "f1":       f1_score(y_te, y_pred, zero_division=0),
        "t_treino_s": t_treino,
    }


def _svm(Xtr, ytr, Xte, yte):
    m = SVC(kernel="rbf", C=1.0, gamma="scale")
    t = time.perf_counter(); m.fit(Xtr, ytr); dt = time.perf_counter() - t
    return _metricas("SVM (RBF)", "clássico", yte, m.predict(Xte), dt)


def _rf(Xtr, ytr, Xte, yte):
    m = RandomForestClassifier(n_estimators=200, random_state=42)
    t = time.perf_counter(); m.fit(Xtr, ytr); dt = time.perf_counter() - t
    return _metricas("Random Forest", "clássico", yte, m.predict(Xte), dt)


def _qsvc(Xtr, ytr, Xte, yte):
    fm = ZZFeatureMap(feature_dimension=N_QUBITS, reps=2)
    kern = FidelityQuantumKernel(
        feature_map=fm, fidelity=ComputeUncompute(sampler=StatevectorSampler()))
    m = QSVC(quantum_kernel=kern)
    t = time.perf_counter(); m.fit(Xtr, ytr); dt = time.perf_counter() - t
    return _metricas("QSVC (kernel quântico)", "quântico", yte, m.predict(Xte), dt)


def _vqc(Xtr, ytr, Xte, yte, seed):
    fm = ZZFeatureMap(feature_dimension=N_QUBITS, reps=2)
    ansatz = RealAmplitudes(num_qubits=N_QUBITS, reps=2)
    np.random.seed(seed)
    m = VQC(feature_map=fm, ansatz=ansatz,
            optimizer=COBYLA(maxiter=60), sampler=StatevectorSampler())
    t = time.perf_counter(); m.fit(Xtr, ytr); dt = time.perf_counter() - t
    return _metricas("VQC (variacional)", "quântico", yte, m.predict(Xte), dt)


RAW = os.path.join(DIR, "robustez_raw.jsonl")


def rodar_seeds(seeds):
    """Roda os 4 modelos para cada seed e ANEXA cada resultado a um JSONL.
    Permite execução em blocos (chunks) em chamadas separadas sem perder dados.
    """
    os.makedirs(DIR, exist_ok=True)
    X, y = preparar_dados(N_QUBITS)
    for s in seeds:
        Xb, yb = subconjunto_balanceado(X, y, N_AMOSTRAS, seed=s)
        Xtr, Xte, ytr, yte = split_treino_teste(Xb, yb, TEST_SIZE, seed=s)
        # pré-processamento ajustado SÓ no treino (sem data leakage)
        Xtr, Xte, _var = preprocessar_split(Xtr, Xte, N_QUBITS)
        print(f"[seed {s}] treino={len(Xtr)} teste={len(Xte)}", flush=True)
        resultados = [_svm(Xtr, ytr, Xte, yte),
                      _rf(Xtr, ytr, Xte, yte),
                      _qsvc(Xtr, ytr, Xte, yte),
                      _vqc(Xtr, ytr, Xte, yte, s)]
        with open(RAW, "a", encoding="utf-8") as f:
            for r in resultados:
                r["seed"] = s
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                print(f"   {r['modelo']:24s} acc={r['acuracia']:.3f} "
                      f"f1={r['f1']:.3f}", flush=True)


def finalizar():
    """Lê o JSONL acumulado e gera CSV/JSON de resumo + figura."""
    df = pd.read_json(RAW, lines=True)
    df = df.drop_duplicates(subset=["modelo", "seed"])
    df.to_csv(os.path.join(DIR, "robustez.csv"), index=False)

    met = ["acuracia", "precisao", "recall", "f1", "t_treino_s"]
    resumo = df.groupby("modelo")[met].agg(["mean", "std"])
    resumo.columns = [f"{a}_{b}" for a, b in resumo.columns]
    resumo = resumo.reset_index()
    resumo.to_csv(os.path.join(DIR, "robustez_resumo.csv"), index=False)
    resumo.to_json(os.path.join(DIR, "robustez_resumo.json"),
                   orient="records", indent=2, force_ascii=False)

    print("\n=== RESUMO (média ± desvio, n=%d sementes) ===" % len(SEEDS))
    for _, row in resumo.iterrows():
        print(f"{row['modelo']:24s} "
              f"acc={row['acuracia_mean']:.3f}±{row['acuracia_std']:.3f} "
              f"prec={row['precisao_mean']:.3f}±{row['precisao_std']:.3f} "
              f"rec={row['recall_mean']:.3f}±{row['recall_std']:.3f} "
              f"f1={row['f1_mean']:.3f}±{row['f1_std']:.3f}")

    _grafico(resumo)
    print("Figura salva em", os.path.join(DIR, "robustez.png"))


def _grafico(resumo):
    ordem = ["SVM (RBF)", "Random Forest", "QSVC (kernel quântico)", "VQC (variacional)"]
    resumo = resumo.set_index("modelo").loc[ordem].reset_index()
    cores = ["#4C72B0", "#4C72B0", "#C44E52", "#C44E52"]
    x = np.arange(len(resumo)); w = 0.38
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w/2, resumo["acuracia_mean"], w, yerr=resumo["acuracia_std"],
           capsize=4, color=cores, label="Acurácia", alpha=0.95)
    ax.bar(x + w/2, resumo["f1_mean"], w, yerr=resumo["f1_std"],
           capsize=4, color=cores, hatch="//", label="F1", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels([m.replace(" (", "\n(") for m in resumo["modelo"]])
    ax.set_ylim(0, 1); ax.set_ylabel("Métrica")
    ax.set_title(f"Robustez multi-semente (n={len(SEEDS)}) — média ± desvio-padrão")
    ax.legend(); plt.tight_layout()
    plt.savefig(os.path.join(DIR, "robustez.png"), dpi=130); plt.close()


if __name__ == "__main__":
    # Uso:
    #   python experimento_robustez.py 0 1        -> roda só essas seeds (anexa)
    #   python experimento_robustez.py finalizar   -> gera resumo + figura
    args = sys.argv[1:]
    if not args:
        rodar_seeds(SEEDS); finalizar()
    elif args[0] == "finalizar":
        finalizar()
    else:
        rodar_seeds([int(a) for a in args])
