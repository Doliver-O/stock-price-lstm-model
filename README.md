# LSTMTrade — Previsão de Preços de Ações com LSTM

## Descrição do Projeto

LSTMTrade é uma aplicação web que permite prever o preço de fechamento das ações de uma empresa utilizando um modelo preditivo de redes neurais Long Short-Term Memory (LSTM). O projeto inclui todo o pipeline, desde o pré-processamento dos dados históricos, treinamento do modelo, até o deploy da API que realiza previsões.

Além disso, a aplicação oferece um dashboard para monitoramento em tempo real das métricas de performance do modelo em produção, como tempo de resposta, uso de CPU e memória.

---

## Tecnologias Utilizadas

- **Flask** — Framework para criação da aplicação web e API REST.  
- **TensorFlow/Keras** — Para desenvolvimento e carregamento do modelo LSTM.  
- **scikit-learn (joblib)** — Para escalonamento dos dados (scaler).  
- **Pandas** e **NumPy** — Manipulação e pré-processamento dos dados.  
- **psutil** — Para monitoramento do uso de recursos do sistema.  
- **Chart.js** — Biblioteca JavaScript para visualização gráfica no frontend.  
- **HTML/CSS/JavaScript** — Frontend da aplicação.  

---

## Funcionalidades

- Upload de arquivo CSV com preços históricos para previsão.  
- Entrada manual de preços históricos via campo texto.  
- Previsão dos próximos 10 dias de preço com base nos últimos 60 dias.  
- API REST para receber dados e retornar previsões.  
- Dashboard web para monitoramento em tempo real de métricas do sistema:  
  - Tempo de resposta das requisições  
  - Uso de CPU  
  - Uso de memória RAM  
- Gráficos interativos para visualização das métricas históricas.  

---

## URLs Base

- Previsão via upload CSV ou entrada manual:  
  `http://localhost:5000/predict`  

- Dashboard de monitoramento:  
  `http://localhost:5000/monitor`  

---

## Endpoints da API

| Endpoint          | Método | Descrição                                  |
|-------------------|--------|--------------------------------------------|
| `/predict_csv`    | POST   | Envia CSV para previsão dos próximos 10 dias. O CSV deve conter uma coluna `close`. |
| `/predict_manual` | POST   | Envia lista manual de preços históricos separados por vírgula. Deve conter 60 valores. |
| `/metrics`        | GET    | Retorna as últimas métricas do sistema (tempo resposta, CPU, memória). |
| `/metrics_history`| GET    | Retorna o histórico das métricas para visualização nos gráficos do dashboard. |


---

## Como Executar

### Pré-requisitos

- Python 3.8+  
- Ambiente virtual (recomendado)  

### Passos

1. Clone o repositório e acesse a pasta:

```bash
git clone https://github.com/seu-usuario/LSTMTrade.git
cd LSTMTrade


# Resumo do Projeto - Previsão de Preços de Ações com LSTM (Apple - AAPL) Arquivo: data_colect.py

## 1. Introdução e Objetivo
Aplicar redes neurais recorrentes LSTM para prever o preço de fechamento das ações da Apple Inc. (AAPL), dividindo o projeto em coleta/preparação dos dados, construção/treinamento do modelo e análise de desempenho.

## 2. Coleta e Preparação dos Dados
- Dados históricos de 01/01/2015 a 01/01/2025 obtidos via biblioteca `yfinance`.
- Considerada apenas a coluna "Close" (preço de fechamento).
- Normalização com `MinMaxScaler` para intervalo [0,1].
- Divisão dos dados: 80% treino, 20% teste.
- Criada janela de observação com 60 timesteps para capturar padrões de curto prazo (~3 meses).

## 3. Construção do Modelo LSTM
- Rede sequencial com:
  - 2 camadas LSTM (50 neurônios cada).
  - 1 camada densa intermediária (25 neurônios).
  - 1 camada densa final (1 neurônio) para previsão.
- Compilado com otimizador Adam e perda mean squared error.
- Treinado com batch size 64, variando épocas (30, 50, 100).

## 4. Previsão e Avaliação
- Previsões feitas no conjunto de teste e reescaladas para valores originais.
- Métricas utilizadas:
  - MAE (Erro Absoluto Médio).
  - RMSE (Raiz do Erro Quadrático Médio).
- Melhores resultados com 100 épocas (MAE 2.07, RMSE 2.74).

## 5. Visualização
- Gráfico comparando valores reais x previstos para avaliação qualitativa da performance do modelo.

## 6. Considerações Finais
- LSTM é eficaz para previsão de séries temporais financeiras.
- Pré-processamento e número de épocas foram decisivos para a performance.
- Pipeline é replicável para outras ações com ajustes mínimos.