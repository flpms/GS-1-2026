# 08 · Visão Computacional — Wildfire Transfer Learning

Classificador de imagens de satélite que separa áreas com risco de incêndio
florestal (`wildfire`) das sem risco (`nowildfire`), usando **transfer learning
com MobileNetV2** pré-treinada na ImageNet.

## Encaixe na cadeia

Este é o elo que faltava em "Observando a Terra": o SENTINELA Orbital (04) hoje
usa dados simulados de focos da NASA FIRMS e INPE; a Visão Computacional dá a
camada anterior, lendo automaticamente as imagens de satélite que alimentam
esse painel. Em produção, cada recorte 350×350 de uma grade de coordenadas
passaria pelo modelo antes de virar alerta na tela.

## O problema

Monitorar grandes extensões territoriais à mão é inviável, então usamos imagens
de satélite e visão computacional para apontar onde há sinal visual de
queimada ou supressão vegetal. O caso de uso prioriza **prevenção**, então o
erro que mais dói é o **falso negativo** — uma área de risco classificada como
segura fica sem monitoramento.

## Dados

- **Dataset:** [Wildfire Prediction Dataset](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) (Kaggle)
- **Splits:** treino, validação e teste já vêm separados; teste com 6.300 imagens
- **Resolução:** 350×350 redimensionada para 224×224 (entrada da MobileNetV2)
- **Classes:** `wildfire` e `nowildfire`

## Modelagem

- Base **MobileNetV2** com pesos da ImageNet, `trainable=False`
- Cabeça: `GlobalAveragePooling2D` → `Dropout(0,3)` → `Dense(1, sigmoid)`
- Otimizador Adam, perda `binary_crossentropy`, 5 épocas
- Augmentation só no treino (rotação 20°, flip horizontal, zoom 0,2);
  validação e teste sem augmentation, para não vazar dado

## Resultados no conjunto de teste

| Métrica | Valor |
|---|---|
| Acurácia | 0,96 |
| ROC AUC | 0,995 |
| Precisão `wildfire` | 0,99 |
| Recall `wildfire` | 0,94 |
| F1 `wildfire` | 0,96 |

O recall de 0,94 na classe `wildfire` é o ponto de atenção: ~6 % das áreas com
risco (cerca de 200 imagens do teste) foram classificadas como seguras. A
sugestão registrada no notebook é **baixar o limiar de decisão** de 0,5 para
0,3, aceitando alguns falsos positivos a mais em troca de capturar mais áreas
de risco — um trade-off coerente com o objetivo preventivo.

## Como rodar

O notebook foi escrito para o Google Colab e baixa o dataset por `kagglehub`.

- **Notebook no Colab:** https://colab.research.google.com/drive/1FZwkb6ehblV7gCAaBcf1uy07KA1wF3OU
- **Vídeo de explicação (YouTube, não listado):** https://youtu.be/NvNXfn5FOYY
- **Arquivo neste repo:** [`GS-Wildfire-Transfer-Learning.ipynb`](GS-Wildfire-Transfer-Learning.ipynb)

Localmente, basta abrir o `.ipynb` em um ambiente com TensorFlow e executar as
células em ordem. As dependências são `tensorflow`, `kagglehub`, `pillow`,
`matplotlib` e `scikit-learn`; o `kagglehub` cuida do download do dataset.

## Conexão com a Governança

Dois pontos do projeto entram direto no Quadro 4 do relatório:

- **Trade-off de limiar:** decidir entre falso positivo e falso negativo é
  decisão de governança, não só de modelagem; documentamos o critério.
- **Atenção a dados:** o dataset é público e bem rotulado, mas qualquer uso
  real precisa validar a representatividade geográfica e temporal das imagens
  antes de virar alerta de evacuação.
