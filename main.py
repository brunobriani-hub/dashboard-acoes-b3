import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Dashboard de Ações da B3",
    layout="wide"
)

# Cabeçalho
st.markdown(
    """
<div style="background-color:#EAF3FA; border-left:6px solid #82B5D8; border-radius:12px; padding:24px; margin-bottom:24px;">
<h1 style="color:#17324D; font-size:32px; margin:0 0 12px;">DASHBOARD DE AÇÕES DA B3</h1>
<p style="color:#365872; font-size:18px; margin:0 0 16px;">Análise de preços e volume de negociação</p>
<p style="color:#17324D; font-size:14px; font-weight:bold; letter-spacing:1px; margin:0;">DESENVOLVIDO POR BRUNO BRIANI DE PAULA</p>
</div>
""",
    unsafe_allow_html=True
)

# Carregamento
arquivo_enviado = st.file_uploader(
    "Envie outro arquivo CSV, se desejar:",
    type=["csv"],
    key="upload_base"
)

arquivo_padrao = Path(__file__).parent / "dados_b3_reais.csv"

if arquivo_enviado is not None:
    fonte = arquivo_enviado
elif arquivo_padrao.exists():
    fonte = arquivo_padrao
else:
    st.info("Coloque dados_b3_reais.csv na pasta ou envie o arquivo.")
    st.stop()

try:
    df = pd.read_csv(fonte)
except Exception as erro:
    st.error(f"Não foi possível ler o CSV: {erro}")
    st.stop()

colunas_obrigatorias = {
    "data", "ticker", "preco_fechamento", "volume"
}

faltantes = colunas_obrigatorias - set(df.columns)

if faltantes:
    st.error(
        "Colunas ausentes: " + ", ".join(sorted(faltantes))
    )
    st.stop()

# Tratamento da base
df["data"] = pd.to_datetime(df["data"], errors="coerce")

for coluna in ["preco_fechamento", "volume"]:
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

df = df.dropna(subset=["data", "ticker", "preco_fechamento"])
df = df[np.isfinite(df["preco_fechamento"])]
df = df[df["preco_fechamento"] > 0].copy()

df["ticker"] = df["ticker"].astype(str).str.strip()
df = df[df["ticker"] != ""]

df = (
    df.sort_values("data")
    .drop_duplicates(subset=["ticker", "data"], keep="last")
)

if df.empty:
    st.warning("Não há registros válidos no arquivo.")
    st.stop()

acoes = sorted(df["ticker"].unique().tolist())

# Formatação em reais
def reais(valor):
    if pd.isna(valor):
        return "Sem dados"
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


aba1, aba2, aba3 = st.tabs([
    "📋 Dados e filtros",
    "📈 Comparação das ações",
    "💰 Simulação"
])

# ==================================================
# ABA 1 — DADOS E FILTROS
# ==================================================
with aba1:
    st.subheader("Filtros")

    acao = st.selectbox(
        "Selecione uma ação:",
        acoes,
        key="acao_dados"
    )

    historico = df[df["ticker"] == acao].copy()

    datas = sorted(historico["data"].dt.date.unique())

    col_inicio, col_fim = st.columns(2)

    inicio = col_inicio.selectbox(
        "Data inicial:",
        datas,
        index=0,
        key="inicio_dados"
    )

    fim = col_fim.selectbox(
        "Data final:",
        datas,
        index=len(datas) - 1,
        key="fim_dados"
    )

    if inicio > fim:
        st.warning("A data inicial deve ser anterior à data final.")

    else:
        periodo = historico[
            (historico["data"].dt.date >= inicio)
            & (historico["data"].dt.date <= fim)
        ].copy()

        # Indicadores calculados antes do filtro por preço
        primeiro = periodo["preco_fechamento"].iloc[0]
        ultimo = periodo["preco_fechamento"].iloc[-1]
        variacao = (ultimo / primeiro - 1) * 100

        st.subheader("Indicadores do período")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Último preço", reais(ultimo))
        c2.metric("Variação do preço", f"{variacao:.2f}%")
        c3.metric(
            "Preço médio",
            reais(periodo["preco_fechamento"].mean())
        )
        c4.metric("Pregões", len(periodo))

        # Gráfico completo do período
        grafico = periodo.set_index("data")[["preco_fechamento"]]
        grafico = grafico.rename(
            columns={"preco_fechamento": "Fechamento"}
        )

        # Calcula a média com o histórico anterior ao período
        historico["Média móvel de 20 pregões"] = (
            historico["preco_fechamento"]
            .rolling(20, min_periods=20)
            .mean()
        )

        medias = historico.set_index("data")[
            "Média móvel de 20 pregões"
        ]

        grafico = grafico.join(medias)

        st.subheader("Preço de fechamento e média móvel")
        st.line_chart(grafico)

        st.subheader("Volume de negociação")
        st.bar_chart(periodo.set_index("data")[["volume"]])

        # Filtro por preço somente para a tabela
        st.subheader("Tabela e filtro por preço")

        minimo = float(periodo["preco_fechamento"].min())
        maximo = float(periodo["preco_fechamento"].max())

        df_filtrado = periodo.copy()

        if minimo < maximo:
            faixa = st.slider(
                "Faixa de preços da tabela (R$):",
                min_value=minimo,
                max_value=maximo,
                value=(minimo, maximo),
                key=f"faixa_tabela_{acao}_{inicio}_{fim}"
            )

            df_filtrado = periodo[
                periodo["preco_fechamento"].between(
                    faixa[0], faixa[1]
                )
            ]

        st.caption(
            "O filtro de preço afeta apenas a tabela. "
            "Os indicadores e gráficos usam todo o período escolhido."
        )

        st.write(f"Registros na tabela: **{len(df_filtrado)}**")

        st.dataframe(
            df_filtrado,
            hide_index=True,
            use_container_width=True
        )

# ==================================================
# ABA 2 — COMPARAÇÃO
# ==================================================
with aba2:
    st.subheader("Comparação entre ações")

    selecionadas = st.multiselect(
        "Escolha as ações:",
        options=acoes,
        default=acoes,
        key="acoes_comparacao"
    )

    modo = st.radio(
        "Tipo de comparação:",
        ["Preço em reais", "Evolução percentual"],
        horizontal=True,
        key="modo_comparacao"
    )

    if not selecionadas:
        st.info("Selecione pelo menos uma ação.")

    else:
        tabela_precos = (
            df[df["ticker"].isin(selecionadas)]
            .pivot(
                index="data",
                columns="ticker",
                values="preco_fechamento"
            )
            .sort_index()
        )

        # Usa datas com cotação para todas as ações selecionadas
        tabela_precos = tabela_precos.dropna()

        if tabela_precos.empty:
            st.warning(
                "Não há datas com preços para todas as ações selecionadas."
            )

        else:
            st.caption(
                "Período comum: "
                f"{tabela_precos.index.min():%d/%m/%Y} a "
                f"{tabela_precos.index.max():%d/%m/%Y}."
            )

            evolucao = (
                tabela_precos.div(tabela_precos.iloc[0]) - 1
            ) * 100

            if modo == "Preço em reais":
                st.line_chart(tabela_precos)
            else:
                st.line_chart(evolucao)
                st.caption(
                    "Todas as ações começam em 0%. "
                    "As linhas mostram a variação em relação ao preço inicial."
                )

            resumo = pd.DataFrame({
                "Preço inicial (R$)": tabela_precos.iloc[0],
                "Preço final (R$)": tabela_precos.iloc[-1],
                "Variação no período (%)": evolucao.iloc[-1]
            })

            resumo.index.name = "Ação"

            st.subheader("Resumo da comparação")

            st.dataframe(
                resumo.sort_values(
                    "Variação no período (%)",
                    ascending=False
                ).round(2),
                use_container_width=True
            )

# ==================================================
# ABA 3 — SIMULAÇÃO
# ==================================================
with aba3:
    st.subheader("Simulação de tendência")

    st.caption(
        "Estatística de tendência linear "
        "dos últimos 60 pregões. Base completa."
    )

    acoes_simulacao = st.multiselect(
        "Ações para simular:",
        options=acoes,
        default=acoes,
        key="acoes_simulacao"
    )

    c1, c2 = st.columns(2)

    valor_investido = c1.number_input(
        "Investimento em cada ação (R$):",
        min_value=0.0,
        value=1000.0,
        step=100.0,
        key="investimento"
    )

    horizonte = c2.slider(
        "Número de pregões projetados:",
        min_value=1,
        max_value=30,
        value=20,
        key="horizonte"
    )

    resultados = []

    for ticker in acoes_simulacao:
        historico = df[df["ticker"] == ticker].tail(60)

        if len(historico) < 60:
            continue

        precos = historico["preco_fechamento"].to_numpy()
        x = np.arange(len(precos))

        intercepto, inclinacao = (
            np.polynomial.polynomial.polyfit(x, precos, deg=1)
        )

        ultimo = float(precos[-1])
        projetado = ultimo + inclinacao * horizonte

        if projetado <= 0:
            continue

        variacao = (projetado / ultimo - 1) * 100
        ganho = valor_investido * variacao / 100

        volatilidade = (
            historico["preco_fechamento"]
            .pct_change(fill_method=None)
            .dropna()
            .std()
            * 100
        )

        resultados.append({
            "Ação": ticker,
            "Data da base": historico["data"].iloc[-1].date(),
            "Último preço (R$)": ultimo,
            "Preço simulado (R$)": projetado,
            "Variação simulada (%)": variacao,
            "Volatilidade diária (%)": volatilidade,
            "Ganho/perda simulado (R$)": ganho,
            "Saldo simulado (R$)": valor_investido + ganho
        })

    if resultados:
        tabela = pd.DataFrame(resultados).sort_values(
            "Variação simulada (%)",
            ascending=False
        )

        st.dataframe(
            tabela.round(2),
            hide_index=True,
            use_container_width=True
        )

        st.subheader("Ganho ou perda simulado em reais")

        st.bar_chart(
            tabela.set_index("Ação")[
                ["Ganho/perda simulado (R$)"]
            ]
        )

    else:
        st.info(
            "Selecione ações com pelo menos 60 pregões válidos."
        )

    st.caption(
        "A simulação começa após a última data de cada ação no CSV. "
        "O valor informado é aplicado separadamente em cada ação, "
        "permitindo frações. Resultados brutos, sem custos e impostos. "
        "O modelo não foi validado para previsão e não representa "
        "recomendação de investimento."
    )

# Rodapé
st.divider()

st.caption(
    "Fonte da base da aula: Yahoo Finance, obtidos pela biblioteca "
    "Python yfinance. Arquivo: dados_b3_reais.csv."
)

st.caption(
    "Dados históricos, sem atualização em tempo real. "
    "Se outro CSV for enviado, sua fonte deve ser verificada."
)