"""
experimento_ruido.py — Viabilidade empírica em hardware NISQ (simulação com ruído).

Motivação: o experimento original roda em simulador IDEAL (sem ruído), e a
análise de viabilidade em hardware quântico atual é apenas argumentativa. Aqui
medimos empiricamente a degradação do QSVC sob ruído, usando o AerSimulator com
um modelo de ruído realista (erros depolarizantes em portas de 1 e 2 qubits +
erro de leitura), em magnitudes próximas às de QPUs supercondutoras atuais
(erro de porta de 2 qubits da ordem de 1%).

Como o sampler com ruído não interpreta blocos de alto nível, o ZZFeatureMap é
transpilado para portas básicas (u, cx, rz, ...) antes da execução.

Níveis de ruído avaliados:
  - ideal      : StatevectorSampler (exato, sem ruído)  -> referência
  - moderado   : ~NISQ atual (1q=0,1% | 2q=1,2% | leitura=2%)
  - alto       : hardware mais ruidoso (1q=0,2% | 2q=2,5% | leitura=4%)

Saídas:
  resultados/ruido.csv / .json
  resultados/ruido.png

Uso: python experimento_ruido.py
"""

import os, sys, json, time, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit import transpile
from qiskit.circuit.library import ZZFeatureMap
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit_aer.primitives import SamplerV2 as AerSampler
from qiskit.primitives import StatevectorSampler
from qiskit_machine_learning.state_fidelities import ComputeUncompute
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from comum import preparar_dados, subconjunto_balanceado, split_treino_teste, preprocessar_split

warnings.filterwarnings("ignore")

N_QUBITS = 4
N_AMOSTRAS = 60          # subconjunto menor: simulação com shots é cara
TEST_SIZE = 0.3
SEEDS = [0, 42]          # 2 sementes para reduzir variância
SHOTS = 512
BASIS = ["u", "cx", "rz", "sx", "x", "h", "p", "ry", "rx", "id"]
DIR = "resultados"

NIVEIS = {
    "ideal":    None,
    "moderado": dict(p1=0.001, p2=0.012, ro=0.02),
    "alto":     dict(p1=0.002, p2=0.025, ro=0.04),
}


def construir_noise_model(p1, p2, ro):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(
        depolarizing_error(p1, 1), ["u", "rz", "sx", "x", "h", "p", "ry", "rx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx"])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - ro, ro], [ro, 1 - ro]]))
    return nm


def fazer_kernel(nivel, seed):
    fm = ZZFeatureMap(feature_dimension=N_QUBITS, reps=2)
    if NIVEIS[nivel] is None:
        sampler = StatevectorSampler()
        fmap = fm
    else:
        nm = construir_noise_model(**NIVEIS[nivel])
        sampler = AerSampler(default_shots=SHOTS, seed=seed,
                             options={"backend_options": {"noise_model": nm}})
        fmap = transpile(fm, basis_gates=BASIS, optimization_level=1)
    return FidelityQuantumKernel(
        feature_map=fmap, fidelity=ComputeUncompute(sampler=sampler))


RAW = os.path.join(DIR, "ruido_raw.jsonl")


def rodar_niveis(niveis):
    os.makedirs(DIR, exist_ok=True)
    X, y = preparar_dados(N_QUBITS)
    for nivel in niveis:
        for s in SEEDS:
            Xb, yb = subconjunto_balanceado(X, y, N_AMOSTRAS, seed=s)
            Xtr, Xte, ytr, yte = split_treino_teste(Xb, yb, TEST_SIZE, seed=s)
            # pré-processamento ajustado SÓ no treino (sem data leakage)
            Xtr, Xte, _var = preprocessar_split(Xtr, Xte, N_QUBITS)
            kern = fazer_kernel(nivel, s)
            m = QSVC(quantum_kernel=kern)
            t = time.perf_counter(); m.fit(Xtr, ytr); dt = time.perf_counter() - t
            yp = m.predict(Xte)
            row = {
                "nivel": nivel, "seed": s,
                "acuracia": accuracy_score(yte, yp),
                "precisao": precision_score(yte, yp, zero_division=0),
                "recall":   recall_score(yte, yp, zero_division=0),
                "f1":       f1_score(yte, yp, zero_division=0),
                "t_treino_s": dt,
            }
            with open(RAW, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"[{nivel:8s} seed {s}] acc={row['acuracia']:.3f} "
                  f"f1={row['f1']:.3f} t={dt:.1f}s", flush=True)


def finalizar():
    df = pd.read_json(RAW, lines=True).drop_duplicates(subset=["nivel", "seed"])
    df.to_csv(os.path.join(DIR, "ruido.csv"), index=False)
    resumo = df.groupby("nivel")[["acuracia", "precisao", "recall", "f1", "t_treino_s"]] \
               .agg(["mean", "std"])
    resumo.columns = [f"{a}_{b}" for a, b in resumo.columns]
    resumo = resumo.reset_index()
    # ordenar ideal -> moderado -> alto
    ordem = {"ideal": 0, "moderado": 1, "alto": 2}
    resumo = resumo.sort_values("nivel", key=lambda c: c.map(ordem)).reset_index(drop=True)
    resumo.to_csv(os.path.join(DIR, "ruido_resumo.csv"), index=False)
    resumo.to_json(os.path.join(DIR, "ruido_resumo.json"),
                   orient="records", indent=2, force_ascii=False)

    print("\n=== RUÍDO: QSVC por nível (média ± desvio, n=%d) ===" % len(SEEDS))
    for _, r in resumo.iterrows():
        print(f"{r['nivel']:8s} acc={r['acuracia_mean']:.3f}±{r['acuracia_std']:.3f} "
              f"f1={r['f1_mean']:.3f}±{r['f1_std']:.3f}")

    _grafico(resumo)
    print("Figura salva em", os.path.join(DIR, "ruido.png"))


def _grafico(resumo):
    x = np.arange(len(resumo)); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - w/2, resumo["acuracia_mean"], w, yerr=resumo["acuracia_std"],
           capsize=4, color="#C44E52", label="Acurácia")
    ax.bar(x + w/2, resumo["f1_mean"], w, yerr=resumo["f1_std"],
           capsize=4, color="#DD8452", label="F1")
    rot = {"ideal": "Ideal\n(statevector)", "moderado": "Ruído moderado\n(~NISQ atual)",
           "alto": "Ruído alto"}
    ax.set_xticks(x); ax.set_xticklabels([rot[n] for n in resumo["nivel"]])
    ax.set_ylim(0, 1); ax.set_ylabel("Métrica")
    ax.set_title("QSVC sob ruído (simulação Aer) — degradação com o ruído NISQ")
    ax.legend(); plt.tight_layout()
    plt.savefig(os.path.join(DIR, "ruido.png"), dpi=130); plt.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        rodar_niveis(list(NIVEIS)); finalizar()
    elif args[0] == "finalizar":
        finalizar()
    else:
        rodar_niveis(args)
