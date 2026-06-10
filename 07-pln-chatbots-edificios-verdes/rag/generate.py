"""Geração da resposta com LLM pequena local (llama3.2 via Ollama).

Monta o prompt com as passagens recuperadas e pede uma resposta fundamentada
apenas no contexto. O enquadramento conecta a autossuficiência dos edifícios
verdes (energia, água, resíduos) com habitats sustentáveis — a mesma tecnologia
que torna um prédio independente de serviços externos é a base para habitats
em ambientes extremos, inclusive espaciais (ponte Terra -> espaço).
"""

import ollama

MODELO_LLM = "llama3.2"

SYSTEM_PROMPT = (
    "Você é um assistente técnico especializado em edifícios verdes e net zero "
    "de energia e água. Responda SEMPRE em português do Brasil, de forma clara e "
    "objetiva, usando exclusivamente as informações do CONTEXTO fornecido. "
    "Se a informação não estiver no contexto, diga explicitamente que não foi "
    "encontrada nos documentos do corpus — não invente dados. "
    "Quando fizer sentido, relacione os conceitos de autossuficiência em energia, "
    "água e resíduos com sua aplicação em habitats sustentáveis e ambientes "
    "extremos (inclusive habitats espaciais), pois é a mesma tecnologia de base."
)


def montar_prompt(pergunta: str, passagens: list[dict]) -> str:
    blocos = []
    for p in passagens:
        blocos.append(f"[Fonte: {p['fonte']} | trecho {p['id_chunk']}]\n{p['texto']}")
    contexto = "\n\n".join(blocos)
    return (
        f"CONTEXTO:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}\n\n"
        "RESPOSTA (fundamentada apenas no contexto acima):"
    )


def gerar_resposta(
    pergunta: str, passagens: list[dict], modelo: str = MODELO_LLM
) -> str:
    prompt = montar_prompt(pergunta, passagens)
    resposta = ollama.chat(
        model=modelo,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resposta["message"]["content"]
