# Dashboard de Ações da B3

Dashboard interativo desenvolvido em Python e Streamlit para explorar preços históricos, comparar ações e simular a continuidade de tendências de preço.

**Autor:** Bruno Briani de Paula

[📊 Acessar o dashboard](https://dashboard-acoes-b3-k3mhdzqy7wr8rpt5k3dytg.streamlit.app/)

## Objetivo

Projeto iniciado a partir de uma base de aula e ampliado com indicadores, gráficos, navegação em abas e simulação de ganhos e perdas em reais.

## Funcionalidades

### Dados e filtros
- Seleção de ação e período.
- Indicadores de preço, variação percentual e quantidade de pregões.
- Gráfico de fechamento com média móvel de 20 pregões.
- Volume de negociação e tabela com filtro por preço.

### Comparação de ações
- Seleção de várias ações.
- Comparação de preços em reais ou evolução percentual.
- Resumo da variação no período comum às ações selecionadas.

### Simulação
- Tendência linear calculada com os últimos 60 pregões.
- Horizonte ajustável de 1 a 30 pregões.
- Investimento hipotético informado pelo usuário.
- Ganho ou perda em reais, saldo simulado e volatilidade diária.

## Tecnologias

Python · Streamlit · pandas · NumPy · yfinance · Git · GitHub

## Fonte dos dados

Dados históricos de PETR4, VALE3, ITUB4, BBAS3, ABEV3 e WEGE3 obtidos do Yahoo Finance pela biblioteca yfinance.

O dashboard utiliza o arquivo CSV disponível no repositório, sem atualização em tempo real. O script `dados.py` permite gerar uma nova base.

## Executar localmente

Com Python instalado, execute na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

Mantenha `dados_b3_reais.csv` na mesma pasta de `main.py`.

Para obter uma nova base, execute opcionalmente:

```bash
python dados.py
```

Esse comando requer internet e substitui o CSV local.

## Limites da análise

A simulação prolonga a tendência linear recente a partir do último preço disponível. O modelo não foi validado para previsão.

Os resultados permitem frações de ação e não incluem custos, impostos ou pagamentos de dividendos. As variações calculadas se referem aos preços registrados no CSV, que podem refletir ajustes do provedor.

O projeto tem finalidade educacional e não constitui recomendação de investimento. Desempenho passado não garante resultados futuros.