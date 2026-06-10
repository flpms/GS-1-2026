"""Ingestão do corpus.

Lê todos os PDFs da pasta `data/`, extrai o texto de cada página e divide o
conteúdo em passagens (chunks) com sobreposição, prontas para virar embeddings.
"""

from pathlib import Path

from pypdf import PdfReader


def carregar_pdfs(pasta_dados: str = "data") -> list[dict]:
    """Lê todos os .pdf da pasta e devolve uma lista {fonte, texto}."""
    documentos: list[dict] = []
    pasta = Path(pasta_dados)

    arquivos = sorted(pasta.glob("*.pdf"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em '{pasta_dados}/'. "
            "Baixe os 4 documentos do corpus (ver README) e coloque-os nessa pasta."
        )

    for caminho_pdf in arquivos:
        leitor = PdfReader(str(caminho_pdf))
        paginas = []
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ""
            paginas.append(texto)
        texto_completo = "\n".join(paginas)
        documentos.append({"fonte": caminho_pdf.name, "texto": texto_completo})
        print(f"  - lido: {caminho_pdf.name} ({len(texto_completo)} caracteres)")

    return documentos


def dividir_em_chunks(
    texto: str, palavras_por_chunk: int = 180, sobreposicao: int = 30
) -> list[str]:
    """Divide um texto em janelas de palavras com sobreposição."""
    palavras = texto.split()
    chunks: list[str] = []
    inicio = 0
    passo = max(1, palavras_por_chunk - sobreposicao)

    while inicio < len(palavras):
        fim = inicio + palavras_por_chunk
        chunk = " ".join(palavras[inicio:fim]).strip()
        if chunk:
            chunks.append(chunk)
        inicio += passo

    return chunks


def construir_passagens(pasta_dados: str = "data") -> list[dict]:
    """Pipeline de ingestão: PDFs -> lista de passagens com metadados."""
    print("Lendo PDFs do corpus...")
    documentos = carregar_pdfs(pasta_dados)

    passagens: list[dict] = []
    for doc in documentos:
        for i, chunk in enumerate(dividir_em_chunks(doc["texto"])):
            passagens.append(
                {"fonte": doc["fonte"], "id_chunk": i, "texto": chunk}
            )

    print(f"Total de passagens geradas: {len(passagens)}")
    return passagens
