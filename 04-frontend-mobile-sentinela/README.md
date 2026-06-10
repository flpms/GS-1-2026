# 04 · Front End & Mobile Development — SENTINELA Orbital

O código desta disciplina vive em um repositório próprio:

**https://github.com/paivazzz/GS_Front**

## Resumo

Dashboard de monitoramento de queimadas e risco climático via satélite, em
Streamlit, com quatro telas: Visão Geral (KPIs nacionais, evolução diária,
ranking de estados e biomas), Mapa de Focos (georreferenciado, colorido pela
potência radiativa), Análise de Risco (um RandomForest classifica o risco por
estado, com fluxo de aprovação humana dos alertas) e Clima (temperatura,
umidade, precipitação e dias sem chuva).

Os dados seguem o formato de APIs reais (NASA FIRMS / INPE para focos, ERA5 /
INMET / OpenWeather para clima), mas são simulados de forma determinística para
rodar offline. A arquitetura em camadas (`providers / pipelines / features /
state / ui`) deixa a troca por dados reais isolada na camada `providers/`.

## Por que está aqui só como link

Já versionado em `paivazzz/GS_Front`, com histórico próprio. Mantemos o link
para preservar autoria e histórico de commits, sem duplicar o código.
