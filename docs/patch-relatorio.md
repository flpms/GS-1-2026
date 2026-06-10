# Patch do relatório — incluir Physical Computing e Visão Computacional

Mudanças a aplicar no Google Doc
[Relatorio_GS2026_Grupo4M_NovaEconomiaEspacial](https://docs.google.com/document/d/1cKUXiPa3DIOzOOLX9pR_nGU8LYH3D-4FsYGJPQezZ90/edit)
para refletir a entrega das duas disciplinas que estavam como pendentes:

- **06 Physical Computing** → **Estação Meteorológica IoT** (`flpms/GS-iot`)
- **08 Visão Computacional** → **GS-Wildfire-Transfer-Learning**

Eu não tenho ferramenta de edição direta de Google Doc, então o patch está
aqui em forma de "encontrar e substituir".

> **Atenção à conclusão:** não mexer no tópico 12. O enunciado proíbe IA gerar
> a conclusão. Quando for escrever a conclusão à mão, lembre-se de que agora
> as nove disciplinas estão integradas.

---

## 1. Quadro 1 (Seção 2 · Visão Geral da Integração)

**Substituir a linha**

| Physical Computing e Cognitive IoT | pendente | camada física e IoT (sem entrega) |

**por**

| Physical Computing e Cognitive IoT | Estação Meteorológica IoT | Camada física: estação de solo, ESP32 com DHT22 e LDR |

**E substituir a linha**

| Visão Computacional | pendente | leitura de imagens de satélite (sem entrega) |

**por**

| Visão Computacional | Wildfire Transfer Learning | Observação da Terra: classifica imagens de satélite |

---

## 2. Parágrafo antes do Quadro 1 (Seção 2)

**Substituir**

> O Quadro 1 resume essa organização, ligando cada disciplina ao seu projeto e
> à sua posição na cadeia. Duas disciplinas, **Physical Computing** e **Visão
> Computacional**, aparecem sem projeto entregue até o fechamento deste
> documento, e a disciplina de Governança trata disso de forma explícita mais
> adiante.

**por**

> O Quadro 1 resume essa organização, ligando cada disciplina ao seu projeto e
> à sua posição na cadeia. As nove disciplinas chegaram com entrega, em alguns
> casos hospedadas em repositórios próprios e referenciadas pelo monorepo para
> preservar autoria e histórico.

---

## 3. Seção 8 inteira — substituir o texto atual

**Substituir o conteúdo da Seção 8** (que hoje diz "Esta disciplina não teve
projeto entregue até o fechamento deste relatório...") **por**

> Esta disciplina pede que a gente coloque a mão na camada física, do circuito
> ao serviço que recebe o dado, e foi exatamente isso que fizemos no projeto
> **Estação Meteorológica IoT**. Em uma cadeia que começa em órbita, esse
> projeto ocupa a posição complementar, o sensor no chão, a peça que mede o
> ambiente local e entrega o dado para o restante do ciclo.
>
> O coração do circuito é um ESP32 com dois sensores, um DHT22 medindo
> temperatura e umidade e um LDR medindo luminosidade, e o caminho do dado é
> exatamente o que a disciplina cobra. O ESP32 lê, formata em JSON e publica
> em um tópico MQTT, um fluxo no Node-RED orquestra o despacho, e o MongoDB
> recebe e guarda. Tudo isso roda também em simulação no Wokwi, o que nos
> liberou para iterar no software sem depender de hardware em mãos, e o
> servidor inteiro vem encaixotado em um Docker Compose, com Node-RED, broker
> MQTT e MongoDB no mesmo arquivo, com um script Node validando os JSONs antes
> de subir.
>
> O que importa para a nossa cadeia é o que esse dado vira depois. Em uma
> economia espacial completa, uma rede de estações de solo como essa serve de
> base para calibrar e validar o que chega dos satélites, alimenta o SENTINELA
> Orbital com clima local em tempo real e poderia até virar fonte de treino
> para classificadores como o de Visão Computacional. Aqui temos um exemplar
> dessa estação, simulado e funcional, mostrando o padrão de fluxo do sensor
> ao banco, que é onde a decisão começa.

---

## 4. Seção 10 inteira — substituir o texto atual

**Substituir o conteúdo da Seção 10** (que hoje diz "Assim como Physical
Computing, a disciplina de Visão Computacional não teve projeto entregue...")
**por**

> Se o SENTINELA Orbital recebe focos de queimada como entrada, a Visão
> Computacional cuida da etapa anterior, ler a imagem do satélite e dizer,
> sozinha, onde há sinal visual de incêndio. O projeto é um classificador
> binário sobre recortes de 350 por 350 pixels, separando áreas com risco,
> wildfire, das áreas sem risco, nowildfire, e foi a escolha que enche o vazio
> que ficava em observação da Terra.
>
> A estratégia técnica é transfer learning. Em vez de treinar uma rede
> convolucional do zero, partimos da MobileNetV2, uma rede já treinada na
> ImageNet, congelamos toda a base e plugamos uma cabeça de classificação
> enxuta, com pooling, dropout e um neurônio sigmoide. Cinco épocas de treino
> bastam para o modelo convergir, em parte porque a rede já chega sabendo
> enxergar bordas, texturas e padrões visuais, em parte porque o dataset
> usado, o Wildfire Prediction Dataset, do Kaggle, já vem com os conjuntos de
> treino, validação e teste bem definidos. No treino aplicamos augmentation,
> rotação, flip e zoom, e tiramos esse augmentation do teste e da validação
> para não vazar dado.
>
> No conjunto de teste, com 6.300 imagens nunca vistas, o modelo entrega 96%
> de acurácia, ROC AUC de 0,995 e precisão de 0,99 para a classe wildfire. A
> leitura honesta, porém, está no recall de 0,94 dessa mesma classe, cerca de
> 6% das áreas de risco passam como seguras, perto de 200 imagens. Esse falso
> negativo é o erro que mais importa quando o objetivo é prevenção, então
> registramos no próprio notebook uma sugestão direta, baixar o limiar de
> decisão de 0,5 para 0,3, aceitando alguns falsos positivos a mais em troca
> de capturar mais áreas críticas. É uma decisão de governança maquiada de
> decisão de modelagem, e por isso volta a aparecer no Quadro 4.

---

## 5. Quadro 3 (Seção 11 · Governança)

**Substituir a linha**

| Physical Computing | Não | Sem projeto entregue até o fechamento |

**por**

| Physical Computing | Sim | Estação meteorológica IoT em ESP32, com fluxo MQTT, Node-RED e MongoDB, simulada em Wokwi |

**E substituir a linha**

| Visão Computacional | Não | Sem projeto entregue até o fechamento |

**por**

| Visão Computacional | Sim | Classificador MobileNetV2 com 96% de acurácia e recall 0,94 para wildfire |

---

## 6. Parágrafo logo abaixo do Quadro 3

**Substituir**

> Dos nove módulos, sete foram integrados e dois ficaram pendentes. Não
> tratamos isso como detalhe de rodapé, porque governar uma cadeia de IA
> começa por saber, sem rodeio, onde estão os buracos. As duas lacunas,
> Physical Computing e Visão Computacional, deixam a cadeia sem a camada
> física de coleta e sem a leitura automática das imagens de satélite, duas
> peças que outros módulos consumiriam se existissem.

**por**

> Dos nove módulos, todos foram integrados. Não tratamos isso como conquista
> em si, e sim como condição mínima do trabalho, e o que vale registrar é
> outra coisa, que cada disciplina entrega uma evidência verificável, no
> código ou em resultado, e que conseguimos descrever, neste relatório, como
> cada peça se encaixa na cadeia. Três projetos ficaram em repositórios
> próprios, o SpaceWatch RPA, o SENTINELA Orbital e a Estação Meteorológica
> IoT, e o monorepo apenas aponta o link, para preservar o histórico de
> commits e a autoria original.

---

## 7. Quadro 4 (Seção 11 · Matriz de riscos)

**Adicionar uma linha nova** ao quadro, abaixo de "Falso alerta ou alerta
tardio":

| Falso negativo em classificação de risco visual | Visão Computacional | Alta | Limiar de decisão calibrado para prevenção (0,3 em vez de 0,5) e revalidação do recall em novas regiões e épocas do ano |

---

## 8. Tópico 13 Links — URL do repositório

**Substituir**

> **Repositório completo da Global Solution (GitHub):** *a publicar*

**por**

> **Repositório completo da Global Solution (GitHub):**
> [github.com/flpms/GS-1-2026](https://github.com/flpms/GS-1-2026)

O link do vídeo continua como "a publicar" até a gravação ficar pronta.

---

## 9. Referências

**Adicionar** ao final da lista de Referências:

> AABA, Abdelghani. **Wildfire Prediction Dataset**. Kaggle, 2023. Disponível
> em: https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset.
> Acesso em: jun. 2026.

---

## Sobre o vídeo do projeto de Visão Computacional

O notebook traz um vídeo explicativo em https://youtu.be/NvNXfn5FOYY. Esse é o
vídeo do projeto de Visão Computacional especificamente, **não** o vídeo de
apresentação da GS (que ainda está como "a publicar" no tópico 13 Links).
Decida se quer citar esse vídeo como material complementar dentro da Seção 10
ou só deixá-lo no notebook. Se houver vídeo equivalente do projeto IoT, mesma
escolha vale para a Seção 8.
