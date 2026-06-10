# 🛰️ Space Connect — Assistente RAG da Nova Economia Espacial

**GS 2026.1 — Disciplina 05: Generative AI & Advanced Nets**
Grupo 4M · FIAP × Forzy

Assistente inteligente baseado em arquitetura **RAG** (Retrieval-Augmented
Generation) capaz de responder perguntas sobre a nova economia espacial —
clima, satélites, agricultura inteligente e monitoramento ambiental — a
partir de documentos científicos reais.

---

## 🎯 O que o projeto faz

O usuário faz uma pergunta em português; o sistema:

1. **Recupera** os trechos mais relevantes de um corpus de documentos
   científicos (busca semântica com embeddings + FAISS);
2. **Gera** uma resposta fundamentada nesses trechos usando um modelo
   generativo local (llama3.2 via Ollama);
3. **Exibe as fontes** usadas (documento + página + relevância), garantindo
   rastreabilidade e evitando alucinações.

### Como cada requisito do enunciado é atendido

| Requisito do enunciado | Onde está implementado |
|---|---|
| Ingestão de documentos | `rag/ingest.py` — lê PDFs, limpa e divide em chunks |
| Geração de embeddings | `rag/embeddings.py` — `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector store p/ recuperação | `rag/vectorstore.py` — FAISS `IndexFlatIP` |
| Modelo generativo | `rag/generate.py` — llama3.2 via Ollama |
| Interface de demonstração | `app.py` — Streamlit |

---

## 📚 Corpus (documentos reais, licença Creative Commons)

| # | Documento | Tema | Fonte |
|---|---|---|---|
| 01 | Applications of Remote Sensing in Precision Agriculture | Agricultura | MDPI *Remote Sensing*, 2020 (CC BY) |
| 02 | Satellite-based time-series of sea-surface temperature since 1980 | Clima | Nature *Scientific Data*, 2024 (CC BY) |
| 03 | Earth Observation Supporting Disaster Risk Reduction | Desastres | MDPI *Remote Sensing*, 2019 (CC BY) |
| 04 | Wide-Field-of-View Space-Based Spectrometer for Climate Monitoring | Clima / Sensores | MDPI *Sensors*, 2022 (CC BY) |

Os PDFs ficam na pasta `corpus/`. Para trocar ou ampliar o corpus, basta
adicionar/remover PDFs nessa pasta e reconstruir o índice.

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado e em execução
- Modelo llama3.2 baixado:
  ```bash
  ollama pull llama3.2
  ```

### Passo a passo

```bash
# 1. (opcional) criar ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. instalar dependências
pip install -r requirements.txt

# 3. construir o índice FAISS a partir do corpus
#    (baixa o modelo de embeddings na primeira vez)
python -m rag.vectorstore

# 4. rodar a interface
streamlit run app.py
```

A aplicação abre no navegador (geralmente em `http://localhost:8501`).

> **Observação:** se você apenas rodar `streamlit run app.py` sem ter
> construído o índice antes, a própria aplicação o constrói na primeira
> execução (pode demorar um pouco mais nessa primeira vez).

---

## 🗂️ Estrutura do projeto

```
gs-rag-espacial/
├── app.py                 # interface Streamlit (demonstração)
├── requirements.txt
├── README.md
├── corpus/                # PDFs do corpus (nova economia espacial)
│   ├── 01_agricultura_sensoriamento_remoto.pdf
│   ├── 02_clima_temperatura_oceano_satelite.pdf
│   ├── 03_desastres_observacao_terra.pdf
│   └── 04_clima_espectrometro_gases.pdf
├── indice/                # índice FAISS + metadados (gerado)
└── rag/
    ├── __init__.py
    ├── ingest.py          # leitura e chunking dos PDFs
    ├── embeddings.py      # geração de embeddings
    ├── vectorstore.py     # índice FAISS e busca semântica
    └── generate.py        # geração da resposta via Ollama
```

---

## 🔍 Exemplos de perguntas para a demonstração

- "Como os satélites ajudam a aumentar a produtividade agrícola?"
- "O que é o índice NDVI e para que serve?"
- "Como os dados de satélite contribuem para a redução de risco de desastres?"
- "Por que medir a temperatura da superfície do mar é importante para o clima?"
- "Quais gases de efeito estufa o espectrômetro espacial consegue detectar?"

---

## 🧠 Detalhes técnicos

- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensões,
  multilíngue PT/EN — importante porque o corpus está em inglês e as
  perguntas são em português).
- **Vector store:** FAISS `IndexFlatIP`. Como os embeddings são normalizados
  (L2 = 1), o produto interno equivale à **similaridade do cosseno**.
- **Chunking:** janelas de ~900 caracteres com 150 de sobreposição, para não
  cortar informações relevantes na fronteira entre trechos.
- **Modelo generativo:** llama3.2 (local, via Ollama) com `temperature=0.2`
  para respostas mais factuais. O prompt de sistema instrui o modelo a
  responder **apenas** com base no contexto recuperado e a citar as fontes.
