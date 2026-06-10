# Chatbot RAG — Edifícios Verdes & Net Zero (energia e água)

**Disciplina 07 — PLN, Chatbots & Virtual Agents** · FIAP × Forzy / Global Solution 2026.1
Grupo 4M — Bruno Lanchariche Fitipaldi Lopes (RM 564129), Filipe Melo da Silva (RM 564571), Rafael de Paiva Ramos (RM 563978)

## O que é

Sistema de perguntas e respostas (RAG) sobre **edifícios verdes e net zero de
energia e água**. O corpus de documentos é transformado em embeddings,
armazenado em um vector database (FAISS) e conectado a uma **LLM de pequeno porte
rodando localmente** (llama3.2 via Ollama), que responde dúvidas em português.

**Enquadramento (ponte Terra → espaço):** as tecnologias que tornam um edifício
autossuficiente em energia, água e resíduos — sem depender de serviços externos —
são a mesma base necessária para habitats sustentáveis em ambientes extremos,
incluindo habitats espaciais (Lua/Marte). O corpus trata de edifícios verdes na
Terra; o contexto conecta isso à autossuficiência exigida fora dela.

## Arquitetura

```
PDFs (corpus)  ->  ingestão/chunking  ->  embeddings MiniLM  ->  FAISS (vector DB)
                                                                       |
                          pergunta  ->  embedding  ->  busca top-k  ---+
                                                                       |
                                              contexto + pergunta  ->  llama3.2 (Ollama)  ->  resposta
```

- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (multilíngue; entende PT mesmo com docs em EN)
- **Vector database:** FAISS `IndexFlatIP` com vetores normalizados (= similaridade de cosseno)
- **LLM local:** `llama3.2` via Ollama
- **Interface:** Streamlit

## Corpus (4 documentos abertos)

| # | Documento | Foco | Fonte |
|---|-----------|------|-------|
| 1 | DOE/FEMP — New Buildings Handbook for Net Zero Energy, Water & Waste | Autossuficiência (energia+água+resíduo), construção nova | Governo EUA (domínio público) |
| 2 | DOE/FEMP — Existing Buildings Handbook for Net Zero Energy, Water & Waste | Mesmo tema, ângulo de retrofit | Governo EUA (domínio público) |
| 3 | MDPI Sustainability (2024) — "Towards Zero: Strategies in Achieving Net-Zero-Energy and Net-Zero-Carbon Buildings" | Estratégias de energia/carbono | MDPI, open access CC BY |
| 4 | MDPI Water (2016) — "Evaluation of Water Efficiency in Green Building in Taiwan" | Eficiência hídrica | MDPI, open access CC BY |

Os links de download estão em `data/LEIA-ME.md`. Baixe os 4 PDFs para a pasta `data/`.

## Como rodar (Windows)

1. **Pré-requisitos:** Python 3.10+ e [Ollama](https://ollama.com) instalados.
   Baixe o modelo:
   ```
   ollama pull llama3.2
   ```

2. **Crie e ative um ambiente virtual (opcional, recomendado):**
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

4. **Baixe os 4 PDFs** do corpus para `data/` (ver `data/LEIA-ME.md`).

5. **Construa o índice vetorial** (uma vez):
   ```
   python construir_indice.py
   ```

6. **Suba a interface:**
   ```
   python -m streamlit run app.py
   ```
   > Use `python -m streamlit ...` para evitar o erro "streamlit não é reconhecido".

## Estrutura

```
gs-pln-edificios-verdes/
├── rag/
│   ├── __init__.py
│   ├── ingest.py        # leitura dos PDFs + chunking
│   ├── embeddings.py    # modelo MiniLM
│   ├── vectorstore.py   # FAISS (build/search/save/load)
│   └── generate.py      # prompt + llama3.2 (Ollama)
├── data/                # PDFs do corpus (ver LEIA-ME.md)
├── indice/              # índice FAISS persistido (gerado pelo script)
├── construir_indice.py  # roda a ingestão e salva o vector DB
├── app.py               # interface Streamlit
├── requirements.txt
└── README.md
```

## Observações técnicas

- `faiss-cpu` está sem versão fixada no `requirements.txt` de propósito, para
  evitar conflitos de versão no Windows.
- O índice fica persistido em `indice/`, atendendo ao requisito de "armazenar o
  corpus em um vector database". Para reindexar (ao trocar PDFs), basta rodar
  `python construir_indice.py` de novo.
- O modelo de embeddings é multilíngue: os documentos estão em inglês, mas as
  perguntas e respostas funcionam em português.
