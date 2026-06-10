"""
Módulo de geração de respostas.

Conecta o contexto recuperado pelo RAG a um modelo generativo local
(llama3.2 via Ollama). O modelo recebe a pergunta do usuário + os trechos
recuperados e responde APENAS com base nesse contexto, citando as fontes.

Isso é o cerne do RAG: o modelo não "inventa" — ele responde fundamentado
nos documentos recuperados, o que reduz alucinações e dá rastreabilidade.
"""

from __future__ import annotations

try:
    import ollama
except ImportError:  # o Ollama só é necessário em tempo de execução da resposta
    ollama = None

from .ingest import Chunk

MODELO_LLM = "llama3.2"

# Instruções de sistema: definem o comportamento do assistente
PROMPT_SISTEMA = """Você é um assistente especializado na nova economia espacial \
(monitoramento climático, agricultura de precisão por satélite, observação da \
Terra e redução de risco de desastres).

Regras importantes:
- Responda SEMPRE em português do Brasil, de forma clara e objetiva.
- Baseie sua resposta EXCLUSIVAMENTE no CONTEXTO fornecido abaixo.
- Se o contexto não contiver a informação necessária, diga explicitamente \
que não há informação suficiente nos documentos disponíveis. Não invente.
- Quando usar uma informação, indique de qual documento ela veio \
(pelo título e página, que aparecem no contexto).
- Seja técnico, mas acessível."""


def montar_contexto(chunks_recuperados: list[tuple[Chunk, float]]) -> str:
    """Formata os trechos recuperados em um bloco de contexto numerado."""
    blocos = []
    for i, (chunk, score) in enumerate(chunks_recuperados, 1):
        cabecalho = (
            f"[Fonte {i}] {chunk.titulo} — página {chunk.pagina} "
            f"(tema: {chunk.tema}, relevância: {score:.2f})"
        )
        blocos.append(f"{cabecalho}\n{chunk.texto}")
    return "\n\n".join(blocos)


def gerar_resposta(
    pergunta: str,
    chunks_recuperados: list[tuple[Chunk, float]],
    modelo: str = MODELO_LLM,
) -> str:
    """
    Gera a resposta final usando o LLM local, fundamentada no contexto.
    """
    contexto = montar_contexto(chunks_recuperados)

    if ollama is None:
        raise RuntimeError(
            "O pacote 'ollama' não está instalado. "
            "Instale com 'pip install ollama' e garanta que o Ollama esteja em execução."
        )

    prompt_usuario = f"""CONTEXTO (trechos recuperados dos documentos):
{contexto}

PERGUNTA DO USUÁRIO:
{pergunta}

Responda à pergunta usando apenas o contexto acima e citando as fontes."""

    resposta = ollama.chat(
        model=modelo,
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": prompt_usuario},
        ],
        options={"temperature": 0.2},  # baixa temperatura = respostas mais factuais
    )
    return resposta["message"]["content"]


def verificar_ollama(modelo: str = MODELO_LLM) -> tuple[bool, str]:
    """
    Verifica se o Ollama está rodando e se o modelo está disponível.
    Retorna (ok, mensagem).
    """
    try:
        if ollama is None:
            return (
                False,
                "O pacote 'ollama' não está instalado. Rode: pip install ollama",
            )
        disponiveis = ollama.list()
        nomes = [m.get("model", m.get("name", "")) for m in disponiveis.get("models", [])]
        if any(modelo in nome for nome in nomes):
            return True, f"Modelo '{modelo}' disponível."
        return (
            False,
            f"Ollama está rodando, mas o modelo '{modelo}' não foi encontrado. "
            f"Rode: ollama pull {modelo}",
        )
    except Exception as exc:
        return (
            False,
            f"Não foi possível conectar ao Ollama: {exc}. "
            "Verifique se o Ollama está instalado e em execução.",
        )
