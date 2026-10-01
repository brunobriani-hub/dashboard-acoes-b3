#%%
# import pandas as pd


# df = pd.read_csv("dados_b3_reais.csv")
# df.head()

#%%
import pandas as pd
import yfinance as yf

# Lista de ações principais da B3 (com .SA para a bolsa de SP)
tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "ABEV3.SA", "WEGE3.SA"]

# Baixar o histórico do último ano
dados = yf.download(tickers, period="1y", group_by="ticker")

# Tratar e organizar a base para formato longo (tidy format)
lista_dfs = []
for t in tickers:
    df_ticker = dados[t][["Close", "Volume"]].copy()
    df_ticker["ticker"] = t.replace(".SA", "")
    df_ticker = df_ticker.reset_index()
    df_ticker.columns = ["data", "preco_fechamento", "volume", "ticker"]
    lista_dfs.append(df_ticker)

df_b3_real = pd.concat(lista_dfs, ignore_index=True)

# Salvar em CSV limpo
df_b3_real.to_csv("dados_b3_reais.csv", index=False)
print("Base real gerada com sucesso!")
