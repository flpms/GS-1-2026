"""
gerar_dataset.py — Gera uma série temporal sintética de telemetria de satélite.

Simula um satélite em órbita terrestre baixa (LEO) com período orbital de ~90 min,
amostrado a cada minuto. São simulados 5 sensores correlacionados ao ciclo
dia/noite orbital, e injetadas anomalias de dois tipos:

  - Anomalia de potência/térmica: queda da tensão da bateria + elevação de temperatura.
  - Degradação de roda de reação: aumento progressivo da vibração.

Cada amostra (minuto) recebe o rótulo binário:
  0 = operação nominal
  1 = anomalia

Saída: dados/telemetria_satelite.csv

Uso:
    python dados/gerar_dataset.py
"""

import os
import numpy as np
import pandas as pd

SEED = 42
N_ORBITAS = 60           # número de órbitas simuladas
MIN_POR_ORBITA = 90      # minutos por órbita (período orbital LEO ~90 min)
CSV_SAIDA = os.path.join(os.path.dirname(__file__), "telemetria_satelite.csv")


def gerar(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = N_ORBITAS * MIN_POR_ORBITA
    t = np.arange(n)

    # Fase orbital (0 a 2*pi a cada órbita) -> ciclo dia/noite (iluminação solar)
    fase = 2 * np.pi * (t % MIN_POR_ORBITA) / MIN_POR_ORBITA
    iluminado = (np.sin(fase) > 0).astype(float)  # 1 = sol, 0 = eclipse

    # --- Sensores nominais -------------------------------------------------
    # Temperatura do painel solar (°C): sobe no sol, cai no eclipse
    temp_painel = 20 + 45 * np.sin(fase) + rng.normal(0, 1.5, n)
    # Tensão da bateria (V): descarrega no eclipse, carrega no sol
    tensao_bateria = 28.0 + 1.2 * np.sin(fase) + rng.normal(0, 0.15, n)
    # Corrente de carga (A): maior quando iluminado
    corrente_carga = 2.0 + 1.5 * iluminado + rng.normal(0, 0.2, n)
    # Temperatura interna (°C): mais estável, leve correlação com painel
    temp_interna = 22 + 6 * np.sin(fase - 0.5) + rng.normal(0, 0.8, n)
    # Velocidade da roda de reação (RPM): controle de atitude, ruído pequeno
    roda_reacao = 3000 + rng.normal(0, 40, n)

    rotulo = np.zeros(n, dtype=int)

    # --- Injeção de anomalias ---------------------------------------------
    # 1) Anomalias de potência/térmica: queda de tensão + pico de temperatura
    n_pot = 14
    for _ in range(n_pot):
        ini = rng.integers(0, n - 60)
        dur = rng.integers(20, 50)
        fim = min(ini + dur, n)
        queda = rng.uniform(1.5, 3.0)
        tensao_bateria[ini:fim] -= queda * np.linspace(0.3, 1.0, fim - ini)
        temp_interna[ini:fim] += rng.uniform(5, 12) * np.linspace(0.3, 1.0, fim - ini)
        rotulo[ini:fim] = 1

    # 2) Degradação da roda de reação: vibração/variância crescente
    n_roda = 10
    for _ in range(n_roda):
        ini = rng.integers(0, n - 60)
        dur = rng.integers(25, 55)
        fim = min(ini + dur, n)
        escala = np.linspace(1, rng.uniform(4, 8), fim - ini)
        roda_reacao[ini:fim] += rng.normal(0, 35, fim - ini) * escala
        rotulo[ini:fim] = 1

    df = pd.DataFrame({
        "minuto": t,
        "fase_orbital": fase,
        "temp_painel": temp_painel,
        "tensao_bateria": tensao_bateria,
        "corrente_carga": corrente_carga,
        "temp_interna": temp_interna,
        "roda_reacao": roda_reacao,
        "rotulo": rotulo,
    })
    return df


def main() -> None:
    df = gerar()
    df.to_csv(CSV_SAIDA, index=False)
    n = len(df)
    n_anom = int(df["rotulo"].sum())
    print(f"Telemetria gerada: {n} amostras (minutos), {N_ORBITAS} órbitas.")
    print(f"Anomalias: {n_anom} ({100*n_anom/n:.1f}%) | Nominais: {n - n_anom}")
    print(f"Arquivo salvo em: {CSV_SAIDA}")


if __name__ == "__main__":
    main()
