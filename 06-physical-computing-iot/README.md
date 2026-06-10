# 06 · Physical Computing, Embedded AI & Cognitive IoT — Estação Meteorológica IoT

O código desta disciplina vive em um repositório próprio:

**https://github.com/flpms/GS-iot**

## Resumo

Estação meteorológica IoT que coleta temperatura, umidade e luminosidade em
campo, publica os dados por MQTT, orquestra o fluxo no Node-RED e persiste em
MongoDB para consulta posterior. O firmware roda em ESP32, com sensor DHT22 no
pino 27 e LDR com resistor de 10 kΩ no pino 35. O circuito é simulado no
Wokwi (`wokwi/diagram.json` + `wokwi/sketch.ino`), de modo que dá para rodar
sem ter o hardware em mãos. O ambiente do servidor vem encaixotado em
`docker-compose.yml`, com Node-RED, broker MQTT e MongoDB de um lado e o
`validate.js` checando os JSONs do outro.

## Encaixe na cadeia

É a camada física da nossa cadeia, a peça que coleta o dado no chão e o
entrega ao restante do ciclo. No fio condutor da Nova Economia Espacial, esta
estação representa o tipo de instrumentação que sustenta a observação local,
uma estação de solo ligada à infraestrutura espacial: o sensor lê o ambiente,
o broker leva o dado adiante, e o que chega no MongoDB pode alimentar tanto
um painel como o SENTINELA Orbital quanto a base de conhecimento de um
assistente como o Space Connect. Fecha o gancho que faltava entre os dados de
satélite e os dados medidos in situ.

## Por que está aqui só como link

Este projeto já está versionado no repositório `flpms/GS-iot` com seu próprio
histórico de commits e dependências de hardware embarcado (PlatformIO, libs
do ESP32). Mantemos o link em vez de duplicar o código, preservando a autoria
e o histórico originais.
