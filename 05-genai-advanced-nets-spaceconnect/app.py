"""
Interface de demonstração — Assistente RAG da Nova Economia Espacial.

GS 2026.1 — Disciplina 05: Generative AI & Advanced Nets
Grupo 4M

Executar com:
    streamlit run app.py

Fluxo da aplicação:
    1. Carrega (ou constrói) o índice FAISS do corpus
    2. Recebe a pergunta do usuário
    3. Recupera os trechos mais relevantes (busca semântica)
    4. Envia pergunta + contexto ao llama3.2 (Ollama)
    5. Exibe a resposta E as fontes utilizadas (rastreabilidade)
"""

from __future__ import annotations

import streamlit as st

from rag.vectorstore import VectorStore, construir_e_salvar, ARQ_FAISS
from rag.generate import gerar_resposta, verificar_ollama, MODELO_LLM

# ----------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Space Connect · Assistente RAG",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo: tema espacial escuro (paleta coesa, tipografia cuidada)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Space+Mono&display=swap');

    .stApp {
        background: radial-gradient(ellipse at top, #141b2d 0%, #0a0e1a 60%);
        color: #e6ebf5;
    }
    h1, h2, h3 { font-family: 'Sora', sans-serif; letter-spacing: -0.5px; }
    .titulo-app {
        font-family: 'Sora', sans-serif; font-weight: 700;
        font-size: 2.4rem; color: #ff4d6d; margin-bottom: 0;
    }
    .subtitulo-app {
        font-family: 'Space Mono', monospace; color: #7a8aa8;
        font-size: 0.95rem; margin-top: 0;
    }
    .fonte-card {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #ff4d6d;
        border-radius: 6px; padding: 12px 16px; margin-bottom: 10px;
    }
    .fonte-meta {
        font-family: 'Space Mono', monospace; font-size: 0.78rem;
        color: #ff9eb1; margin-bottom: 6px;
    }
    .fonte-texto { font-size: 0.86rem; color: #c2cce0; line-height: 1.5; }
    .stChatMessage { background: rgba(255,255,255,0.03); border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Carregamento do índice (cacheado entre execuções)
# ----------------------------------------------------------------------
@st.cache_resource(show_spinner="Carregando índice do corpus...")
def carregar_store() -> VectorStore:
    """Carrega o índice FAISS; constrói se ainda não existir."""
    if ARQ_FAISS.exists():
        return VectorStore.carregar()
    return construir_e_salvar()


# ----------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------
st.markdown('<p class="titulo-app">🛰️ Space Connect</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitulo-app">Assistente RAG · Nova Economia Espacial · '
    "GS 2026.1 — Generative AI &amp; Advanced Nets</p>",
    unsafe_allow_html=True,
)
st.divider()

# ----------------------------------------------------------------------
# Barra lateral: status e configurações
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    top_k = st.slider(
        "Trechos recuperados (k)",
        min_value=2, max_value=8, value=4,
        help="Quantos trechos do corpus alimentam o modelo a cada pergunta.",
    )

    st.subheader("📚 Corpus")
    st.markdown(
        "- Agricultura de precisão por satélite\n"
        "- Temperatura do mar (clima, 1980+)\n"
        "- Observação da Terra p/ desastres\n"
        "- Espectrômetro espacial de gases"
    )

    st.subheader("🤖 Status do modelo")
    ok_ollama, msg_ollama = verificar_ollama()
    if ok_ollama:
        st.success(f"Ollama · {MODELO_LLM} pronto")
    else:
        st.warning(msg_ollama)

    if st.button("🔄 Reconstruir índice"):
        st.cache_resource.clear()
        construir_e_salvar()
        st.success("Índice reconstruído!")
        st.rerun()

# ----------------------------------------------------------------------
# Estado da conversa
# ----------------------------------------------------------------------
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

store = carregar_store()

# Exibe histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fontes"):
            with st.expander("📎 Fontes utilizadas"):
                for fonte in msg["fontes"]:
                    st.markdown(
                        f'<div class="fonte-card">'
                        f'<div class="fonte-meta">{fonte["meta"]}</div>'
                        f'<div class="fonte-texto">{fonte["texto"]}</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# ----------------------------------------------------------------------
# Entrada do usuário
# ----------------------------------------------------------------------
pergunta = st.chat_input("Pergunte sobre clima, satélites, agricultura, desastres...")

if pergunta:
    # Mostra a pergunta
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Recupera contexto + gera resposta
    with st.chat_message("assistant"):
        with st.spinner("Recuperando contexto e gerando resposta..."):
            recuperados = store.buscar(pergunta, k=top_k)

            if not ok_ollama:
                resposta = (
                    "⚠️ O modelo generativo (Ollama/llama3.2) não está disponível, "
                    "então não consigo gerar a resposta final. Mesmo assim, recuperei "
                    "os trechos mais relevantes do corpus — veja as fontes abaixo.\n\n"
                    f"_{msg_ollama}_"
                )
            else:
                try:
                    resposta = gerar_resposta(pergunta, recuperados)
                except Exception as exc:
                    resposta = f"Ocorreu um erro ao gerar a resposta: {exc}"

        st.markdown(resposta)

        # Prepara as fontes para exibição
        fontes = [
            {
                "meta": f"{c.titulo} · p.{c.pagina} · tema: {c.tema} · "
                f"relevância: {s:.2f}",
                "texto": c.texto[:400] + ("..." if len(c.texto) > 400 else ""),
            }
            for c, s in recuperados
        ]
        with st.expander("📎 Fontes utilizadas"):
            for fonte in fontes:
                st.markdown(
                    f'<div class="fonte-card">'
                    f'<div class="fonte-meta">{fonte["meta"]}</div>'
                    f'<div class="fonte-texto">{fonte["texto"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.session_state.mensagens.append(
        {"role": "assistant", "content": resposta, "fontes": fontes}
    )
