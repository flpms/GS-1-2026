# 01 · AI for Robotic Process Automation — SpaceWatch RPA

O código desta disciplina vive em um repositório próprio:

**https://github.com/paivazzz/GS_RPA**

## Resumo

Robô de automação que faz, sozinho, o ciclo diário de acompanhamento de
asteroides próximos da Terra. Busca os dados do dia na API da NASA (NeoWs),
calcula o risco de cada asteroide (0–100), classifica em BAIXO/MÉDIO/ALTO/CRÍTICO,
guarda em banco SQLite sem duplicar histórico, gera a planilha
`relatorio_asteroides.xlsx` e ainda agrupa os asteroides por perfil com K-Means.

Integra três tópicos da disciplina: **REST API** (`nasa_client.py`),
**Arquivos & Database** (`repository.py`) e **Execução & Agendamento**
(`agendamento.py`). Tem ainda dashboard web (Streamlit) e API REST (FastAPI).

## Por que está aqui só como link

Este projeto já está versionado no repositório `paivazzz/GS_RPA` com seu próprio
histórico de commits. Mantemos o link em vez de duplicar o código, preservando a
autoria e o histórico originais.
