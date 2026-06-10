# QML aplicado a telemetria de satélite — detecção de anomalias

Aplicação de **Quantum Machine Learning (QML)** com **Qiskit** à detecção de anomalias
em telemetria de satélite, comparada a um **baseline clássico** equivalente. Avalia
precisão, eficiência e viabilidade em hardware quântico atual (NISQ).

## Problema
Classificação binária (operação **nominal** vs. **anomalia**) sobre janelas da série
temporal de 5 sensores de um satélite em órbita baixa (LEO). Anomalias simuladas:
falha de potência/térmica e degradação de roda de reação.

## Modelos comparados
| Tipo | Modelo |
|------|--------|
| Clássico | SVM (kernel RBF), Random Forest |
| Quântico | QSVC (kernel quântico, FidelityQuantumKernel + ZZFeatureMap), VQC (variacional, ZZFeatureMap + RealAmplitudes + COBYLA) |

Tudo executado no simulador **Aer**. Dimensionalidade reduzida por PCA a 4 componentes
(= 4 qubits).

## Como executar
```bash
pip install -r requirements.txt
python dados/gerar_dataset.py     # gera dados/telemetria_satelite.csv
python experimento.py             # roda clássico + QML, salva resultados/ e gráficos
```

## Estrutura
```
qml-satelite/
├── dados/
│   ├── gerar_dataset.py          # gerador da telemetria sintética
│   └── telemetria_satelite.csv   # dataset (gerado)
├── features.py                   # janelamento + extração de atributos
├── baseline_classico.py          # SVM RBF + Random Forest
├── qml_modelo.py                 # QSVC + VQC (Qiskit)
├── experimento.py                # orquestra, compara, gera tabela + gráficos
├── resultados/                   # resultados.csv/json + PNGs (gerado)
├── relatorio_tecnico_qml.docx    # relatório técnico
└── requirements.txt
```

## Principais resultados (resumo)
No subconjunto reduzido (4 qubits), o QSVC foi competitivo em acurácia (0,833) e F1
(0,812), mas ~4 ordens de grandeza mais lento que os clássicos. No dataset completo, o
Random Forest clássico atinge 0,932 de acurácia em frações de segundo. Conclusão: em
hardware NISQ atual, o baseline clássico é a opção viável. Detalhes e análise crítica
no relatório técnico.
