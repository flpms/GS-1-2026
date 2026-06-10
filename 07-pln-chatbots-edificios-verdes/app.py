"""Interface de demonstração (Streamlit).

Chatbot que responde dúvidas sobre edifícios verdes e net zero (energia e água)
recuperando trechos do corpus (FAISS) e gerando a resposta com llama3.2 local.

Execução:
    python -m streamlit run app.py
"""

import streamlit as st

from rag.embeddings import Embedder
from rag.vectorstore import VectorStore
from rag.generate import gerar_resposta, MODELO_LLM

st.set_page_config(page_title="Chatbot — Edifícios Verdes & Net Zero", page_icon="🌱")


@st.cache_resource(show_spinner="Carregando modelo e índice...")
def carregar_componentes():
    embedder = Embedder()
    store = VectorStore()
    store.carregar("indice")
    return embedder, store


st.title("🌱 Chatbot — Edifícios Verdes & Net Zero")
st.caption(
    "RAG local sobre energia e água em edifícios sustentáveis · "
    "embeddings MiniLM + FAISS + llama3.2 (Ollama) · FIAP × Forzy / Disciplina 07"
)

with st.expander("Sobre este projeto"):
    st.markdown(
        "Corpus de **edifícios verdes e net zero (energia e água)** transformado em "
        "embeddings, armazenado em um vector database (FAISS) e conectado a uma LLM "
        "de pequeno porte rodando localmente. As mesmas tecnologias que tornam um "
        "edifício autossuficiente em energia, água e resíduos são a base para "
        "**habitats sustentáveis em ambientes extremos**, incluindo habitats espaciais."
    )

try:
    embedder, store = carregar_componentes()
except Exception as e:
    st.error(f"Não foi possível carregar o índice: {e}")
    st.info("Rode `python construir_indice.py` antes de iniciar a interface.")
    st.stop()

with st.sidebar:
    st.header("Configurações")
    k = st.slider("Trechos recuperados (k)", min_value=2, max_value=8, value=4)
    st.markdown(f"**Modelo de geração:** `{MODELO_LLM}`")
    st.markdown("**Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2`")

pergunta = st.text_input(
    "Faça uma pergunta sobre edifícios verdes / net zero:",
    placeholder="Ex.: O que é um edifício net zero de energia?",
)

if st.button("Perguntar", type="primary") and pergunta.strip():
    with st.spinner("Buscando trechos relevantes e gerando resposta..."):
        vetor = embedder.codificar(pergunta, normalizar=True)
        passagens = store.buscar(vetor, k=k)
        resposta = gerar_resposta(pergunta, passagens)

    st.subheader("Resposta")
    st.write(resposta)

    st.subheader("Fontes recuperadas")
    for i, p in enumerate(passagens, start=1):
        with st.expander(f"{i}. {p['fonte']} (similaridade {p['score']:.3f})"):
            st.write(p["texto"])
