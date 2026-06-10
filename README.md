# Nova Economia Espacial — Portfólio Integrado de IA · Grupo 4M

**Global Solution 2026.1 — FIAP × Forzy**

Este repositório reúne os projetos das disciplinas do semestre sob um único fio
condutor: a **nova economia espacial**. Em vez de oito trabalhos soltos, tratamos
o tema como uma cadeia, da órbita até o solo, e cada disciplina entra como um elo
dessa cadeia. A disciplina de Governança fecha o conjunto, avaliando o que de fato
se integrou e sob quais regras isso deveria operar.

## Integrantes

| Nome | RM |
|------|----|
| Bruno Lanchariche Fitipaldi Lopes | 564129 |
| Filipe Melo da Silva | 564571 |
| Rafael de Paiva Ramos | 563978 |

## O fio condutor

A economia espacial não é só foguete. É um ciclo de dados: um satélite gera
telemetria em órbita, sensores observam a Terra, esses dados viram alerta para
quem está na ponta, e o conhecimento acumulado vira assistente para tomar decisão.
Cada disciplina cobre uma etapa desse ciclo.

| # | Disciplina | Projeto | O que faz | Onde está |
|---|------------|---------|-----------|-----------|
| 01 | AI for Robotic Process Automation | **SpaceWatch RPA** | Robô que coleta asteroides próximos da Terra (NASA NeoWs), pontua risco, salva em banco e gera planilha | [github.com/paivazzz/GS_RPA](https://github.com/paivazzz/GS_RPA) |
| 02 | Cluster Computing, Neuromórfica & Supercomputadores | **NeuroSpace Alert** | Sensor neuromórfico de baixo consumo que detecta tempestade marciana processando na borda | `02-cluster-neuromorfica-neurospace/` |
| 03 | Computação Quântica & IA | **QML — Telemetria de Satélite** | Detecção de anomalias em telemetria de satélite LEO, comparando QSVC/VQC com baseline clássico | `03-computacao-quantica-qml-satelite/` |
| 04 | Front End & Mobile Development | **SENTINELA Orbital** | Dashboard de queimadas e risco climático via satélite (NASA FIRMS/INPE), com aprovação humana de alertas | [github.com/paivazzz/GS_Front](https://github.com/paivazzz/GS_Front) |
| 05 | Generative AI & Advanced Nets | **Space Connect** | Assistente RAG sobre a nova economia espacial, com citação de fontes | `05-genai-advanced-nets-spaceconnect/` |
| 06 | Physical Computing, Embedded AI & Cognitive IoT | *(pendente)* | — | `06-physical-computing-iot/` |
| 07 | PLN, Chatbots & Virtual Agents | **Edifícios Verdes & Net Zero** | Chatbot RAG sobre autossuficiência de energia e água, ponte Terra → habitats espaciais | `07-pln-chatbots-edificios-verdes/` |
| 08 | Visão Computacional | **Wildfire Transfer Learning** | Classificação de imagens de satélite (`wildfire` vs `nowildfire`) com MobileNetV2 — acurácia 96 %, ROC AUC 0,995 | `08-visao-computacional/` |
| 09 | Governança em IA & Business Analytics | **Relatório de Integração** | Costura todos os módulos, avalia riscos, vieses e aderência aos ODS | `09-governanca/` |

## Como cada elo se conecta

- **Em órbita:** o QML (03) vigia a saúde do próprio satélite, enquanto o sensor neuromórfico (02) leva a mesma lógica de "só avisa quando importa" para uma missão tripulada em Marte.
- **Observando a Terra:** o SpaceWatch (01) monitora o que vem do espaço em direção à Terra (asteroides), a Visão Computacional (08) lê automaticamente as imagens de satélite e classifica risco de queimada, e o SENTINELA Orbital (04) consome esse sinal para gerar alerta com revisão humana.
- **Conhecimento e decisão:** o Space Connect (05) responde perguntas sobre o setor a partir de documentos científicos reais, e o chatbot de edifícios verdes (07) conecta a autossuficiência terrestre à exigida em habitats fora da Terra.
- **Governança (09):** o elo que olha para os oito anteriores e pergunta quem responde quando a IA erra, onde há viés, e o que ficou de fora.

## Links

- **Vídeo (YouTube, não listado):** _a publicar — ver `docs/`_
- **Repositório (este):** _a publicar_
- **SpaceWatch RPA:** https://github.com/paivazzz/GS_RPA
- **SENTINELA Orbital (Front):** https://github.com/paivazzz/GS_Front

## Estrutura

```
GS2026_4M_NovaEconomiaEspacial/
├── 01-rpa-spacewatch/                 # link para o repo GS_RPA
├── 02-cluster-neuromorfica-neurospace/
├── 03-computacao-quantica-qml-satelite/
├── 04-frontend-mobile-sentinela/      # link para o repo GS_Front
├── 05-genai-advanced-nets-spaceconnect/
├── 06-physical-computing-iot/         # pendente
├── 07-pln-chatbots-edificios-verdes/
├── 08-visao-computacional/            # Wildfire Transfer Learning (MobileNetV2)
├── 09-governanca/                     # relatório de integração (ABNT/FIAP)
├── docs/                              # roteiro do vídeo e apoio
└── README.md
```

---

Projeto acadêmico da Global Solution FIAP 2026.1. Sistemas e dados de demonstração
são fictícios ou simulados quando indicado em cada projeto.
