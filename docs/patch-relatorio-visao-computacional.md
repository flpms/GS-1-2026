# Patch do relatório — incluir Visão Computacional

Mudanças a aplicar no Google Doc
[Relatorio_GS2026_Grupo4M_NovaEconomiaEspacial](https://docs.google.com/document/d/1cKUXiPa3DIOzOOLX9pR_nGU8LYH3D-4FsYGJPQezZ90/edit)
para refletir a entrega do projeto **GS-Wildfire-Transfer-Learning** na
disciplina de Visão Computacional. Eu não tenho ferramenta de edição direta de
Google Doc, então o patch está aqui em forma de "encontrar e substituir".

> **Atenção à conclusão:** não mexer no tópico 12. O enunciado proíbe IA gerar
> a conclusão. Quando você for escrever a conclusão à mão, lembre-se de incluir
> a Visão Computacional nas reflexões.

---

## 1. Quadro 1 (Seção 2 · Visão Geral da Integração)

**Substituir a linha**

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
> à sua posição na cadeia. Uma disciplina, **Physical Computing**, aparece sem
> projeto entregue até o fechamento deste documento, e a disciplina de
> Governança trata disso de forma explícita mais adiante.

---

## 3. Seção 10 inteira — substituir o texto atual

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

## 4. Quadro 3 (Seção 11 · Governança)

**Substituir a linha**

| Visão Computacional | Não | Sem projeto entregue até o fechamento |

**por**

| Visão Computacional | Sim | Classificador MobileNetV2 com 96% de acurácia e recall 0,94 para wildfire |

---

## 5. Parágrafo logo abaixo do Quadro 3

**Substituir**

> Dos nove módulos, sete foram integrados e dois ficaram pendentes. Não
> tratamos isso como detalhe de rodapé, porque governar uma cadeia de IA
> começa por saber, sem rodeio, onde estão os buracos. As duas lacunas,
> Physical Computing e Visão Computacional, deixam a cadeia sem a camada
> física de coleta e sem a leitura automática das imagens de satélite, duas
> peças que outros módulos consumiriam se existissem.

**por**

> Dos nove módulos, oito foram integrados e um ficou pendente. Não tratamos
> isso como detalhe de rodapé, porque governar uma cadeia de IA começa por
> saber, sem rodeio, onde estão os buracos. A lacuna é Physical Computing, e
> deixa a cadeia sem a camada física de coleta de sensores em campo, uma peça
> que outros módulos consumiriam se existisse.

---

## 6. Quadro 4 (Seção 11 · Matriz de riscos)

**Adicionar uma linha nova** ao quadro, abaixo de "Falso alerta ou alerta
tardio":

| Falso negativo em classificação de risco visual | Visão Computacional | Alta | Limiar de decisão calibrado para prevenção (0,3 em vez de 0,5) e revalidação do recall em novas regiões e épocas do ano |

---

## 7. Referências

**Adicionar** ao final da lista de Referências:

> AABA, Abdelghani. **Wildfire Prediction Dataset**. Kaggle, 2023. Disponível
> em: https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset.
> Acesso em: jun. 2026.

---

## Sobre o vídeo do projeto de Visão Computacional

O notebook traz um vídeo explicativo em https://youtu.be/NvNXfn5FOYY. Esse é o
vídeo do projeto de Visão Computacional especificamente, **não** o vídeo de
apresentação da GS (que ainda está como "a publicar" no tópico 13 Links). Não
mexi nele. Decida se quer citar esse vídeo como material complementar dentro
da Seção 10 ou só deixá-lo no notebook.
