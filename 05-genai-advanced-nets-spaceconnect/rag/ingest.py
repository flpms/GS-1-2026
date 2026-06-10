"""
Módulo de ingestão de documentos.

Responsável por:
  1. Ler os PDFs da pasta corpus/
  2. Extrair o texto de cada página
  3. Dividir o texto em chunks (trechos) com sobreposição
  4. Guardar metadados (documento de origem, página) para rastreabilidade

A divisão em chunks é importante para o RAG: trechos menores produzem
embeddings mais "focados", o que melhora a precisão da recuperação.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader


# Mapeia o nome do arquivo para um título e tema legíveis (para exibição)
TITULOS_DOCUMENTOS = {
    "01_agricultura_sensoriamento_remoto.pdf": (
        "Aplicações de Sensoriamento Remoto na Agricultura de Precisão",
        "Agricultura",
    ),
    "02_clima_temperatura_oceano_satelite.pdf": (
        "Série Temporal de Temperatura da Superfície do Mar por Satélite (1980+)",
        "Clima",
    ),
    "03_desastres_observacao_terra.pdf": (
        "Observação da Terra para Redução de Risco de Desastres",
        "Desastres",
    ),
    "04_clima_espectrometro_gases.pdf": (
        "Espectrômetro Espacial para Monitoramento Climático de Gases",
        "Clima / Sensores",
    ),
}


@dataclass
class Chunk:
    """Representa um trecho de documento pronto para virar embedding."""
    texto: str
    documento: str          # nome do arquivo de origem
    titulo: str             # título legível
    tema: str               # tema (Agricultura, Clima, Desastres...)
    pagina: int             # página de origem (1-indexada)
    chunk_id: int           # id sequencial global


def _limpar_texto(texto: str) -> str:
    """Normaliza espaços em branco e remove quebras de linha artificiais."""
    # junta hifenização de fim de linha: "agri-\ncultura" -> "agricultura"
    texto = re.sub(r"-\s*\n\s*", "", texto)
    # troca quebras de linha por espaço
    texto = re.sub(r"\s*\n\s*", " ", texto)
    # colapsa espaços múltiplos
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.strip()


def _dividir_em_chunks(
    texto: str,
    tamanho: int = 900,
    sobreposicao: int = 150,
) -> list[str]:
    """
    Divide um texto em janelas de ~tamanho caracteres com sobreposição.

    A sobreposição evita que uma informação relevante seja "cortada" na
    fronteira entre dois chunks, o que prejudicaria a recuperação.
    """
    palavras = texto.split()
    if not palavras:
        return []

    chunks: list[str] = []
    inicio = 0
    # estimativa: ~6 caracteres por palavra (média PT/EN)
    palavras_por_chunk = max(1, tamanho // 6)
    palavras_sobrepostas = max(0, sobreposicao // 6)
    passo = max(1, palavras_por_chunk - palavras_sobrepostas)

    while inicio < len(palavras):
        fim = inicio + palavras_por_chunk
        trecho = " ".join(palavras[inicio:fim])
        if len(trecho.strip()) > 50:  # ignora trechos muito curtos
            chunks.append(trecho)
        inicio += passo

    return chunks


def carregar_corpus(pasta_corpus: str | Path = "corpus") -> list[Chunk]:
    """
    Lê todos os PDFs da pasta de corpus e devolve a lista completa de chunks.
    """
    pasta = Path(pasta_corpus)
    if not pasta.exists():
        raise FileNotFoundError(
            f"Pasta de corpus não encontrada: {pasta.resolve()}"
        )

    pdfs = sorted(pasta.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em {pasta.resolve()}. "
            "Coloque os documentos do corpus nessa pasta."
        )

    todos_chunks: list[Chunk] = []
    chunk_id = 0

    for caminho_pdf in pdfs:
        nome = caminho_pdf.name
        titulo, tema = TITULOS_DOCUMENTOS.get(
            nome, (nome.replace(".pdf", ""), "Geral")
        )

        try:
            reader = PdfReader(str(caminho_pdf))
        except Exception as exc:  # pragma: no cover
            print(f"  [aviso] Falha ao ler {nome}: {exc}")
            continue

        for n_pagina, pagina in enumerate(reader.pages, start=1):
            texto_bruto = pagina.extract_text() or ""
            texto = _limpar_texto(texto_bruto)
            if len(texto) < 100:
                continue  # página sem texto útil (capa, figura etc.)

            for trecho in _dividir_em_chunks(texto):
                todos_chunks.append(
                    Chunk(
                        texto=trecho,
                        documento=nome,
                        titulo=titulo,
                        tema=tema,
                        pagina=n_pagina,
                        chunk_id=chunk_id,
                    )
                )
                chunk_id += 1

        print(f"  [ok] {nome}: {len(reader.pages)} páginas processadas")

    print(f"\n  Total de chunks gerados: {len(todos_chunks)}")
    return todos_chunks


if __name__ == "__main__":
    # Teste rápido de ingestão
    print("Carregando corpus...\n")
    chunks = carregar_corpus()
    if chunks:
        print("\nExemplo de chunk:")
        c = chunks[len(chunks) // 2]
        print(f"  Documento: {c.titulo} (p.{c.pagina}, tema={c.tema})")
        print(f"  Texto: {c.texto[:200]}...")
