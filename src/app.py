# src/app.py
import io
from datetime import date

import pandas as pd
import streamlit as st

from load_data import load_sales, get_filter_options
from transform import (
    apply_filters,
    calc_kpis,
    vendas_mensais,
    top_produtos,
    distribuicao_canal,
    distribuicao_regiao,
)
from charts import chart_vendas_mensais, chart_top_produtos, chart_distribuicao

st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# ---------- Helpers ----------
@st.cache_data(show_spinner=False)
def _load_base():
    df = load_sales()
    opts = get_filter_options(df)
    return df, opts


def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue().encode("utf-8")


# ---------- Header ----------
st.title("📊 Dashboard de Vendas")
st.caption("Explora vendas por período, categoria, região/canal. Vê KPIs, gráficos e exporta os dados filtrados.")

# ---------- Load ----------
with st.spinner("A carregar dados..."):
    sales, options = _load_base()

if sales.empty:
    st.warning("Sem dados para apresentar. Garante que a BD/CSV tem registos.")
    st.stop()

# ---------- Sidebar (Filtros) ----------
st.sidebar.header("Filtros")

# Datas
dmin = options["date_min"] or date(2023, 1, 1)
dmax = options["date_max"] or date.today()
date_range = st.sidebar.date_input(
    "Intervalo de datas",
    value=(dmin, dmax),
    min_value=dmin,
    max_value=dmax,
)

# Categorias / Regiões / Canais
cats = st.sidebar.multiselect("Categoria", options["categories"])
regs = st.sidebar.multiselect("Região", options["regions"])
chans = st.sidebar.multiselect("Canal", options["channels"])

# Pesquisa por cliente (livre)
search_customer = st.sidebar.text_input("Procurar cliente (texto livre)")

# Top N (para gráfico de barras)
top_n = st.sidebar.slider("Top N produtos", min_value=3, max_value=20, value=10, step=1)

# Pizza por: Canal/Região
pie_choice = st.sidebar.radio("Gráfico de distribuição", ["Canal", "Região"], horizontal=True)

# ---------- Aplicar filtros ----------
date_tuple = None
if isinstance(date_range, tuple) and len(date_range) == 2:
    date_tuple = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))

filtered = apply_filters(
    sales,
    date_range=date_tuple,
    categories=cats or None,
    regions=regs or None,
    channels=chans or None,
    search_customer=search_customer or None,
)

st.markdown("### Resultados filtrados")
st.caption(f"{len(filtered)} registos encontrados.")

if filtered.empty:
    st.info("Nenhum registo corresponde aos filtros atuais. Ajusta os filtros na barra lateral.")
    st.stop()

# ---------- KPIs ----------
kpis = calc_kpis(filtered)
col1, col2, col3 = st.columns(3)
col1.metric("💶 Faturação Total", f"€ {kpis['total']:,.2f}".replace(",", " ").replace(".", ","))
col2.metric("🧾 Nº de Vendas", f"{kpis['num_vendas']}")
col3.metric("🎟️ Ticket Médio", f"€ {kpis['ticket_medio']:,.2f}".replace(",", " ").replace(".", ","))

st.markdown("---")

# ---------- Gráficos ----------
# Linha: evolução mensal
mensal = vendas_mensais(filtered)
st.subheader("Evolução Mensal")
st.plotly_chart(chart_vendas_mensais(mensal), use_container_width=True)

# Barras: top produtos
top = top_produtos(filtered, n=top_n)
st.subheader(f"Top {top_n} Produtos por Faturação")
st.plotly_chart(chart_top_produtos(top), use_container_width=True)

# Pizza: canal/região
st.subheader("Distribuição")
if pie_choice == "Canal":
    pie_df = distribuicao_canal(filtered)
    st.plotly_chart(chart_distribuicao(pie_df, "channel", "Distribuição por Canal"), use_container_width=True)
else:
    pie_df = distribuicao_regiao(filtered)
    st.plotly_chart(chart_distribuicao(pie_df, "region", "Distribuição por Região"), use_container_width=True)

st.markdown("---")

# ---------- Tabela + Export ----------
st.subheader("Tabela de Dados (Filtrados)")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv_bytes = _df_to_csv_bytes(filtered)
st.download_button(
    label="⬇️ Exportar CSV (dados filtrados)",
    data=csv_bytes,
    file_name="vendas_filtradas.csv",
    mime="text/csv",
)

# ---------- Rodapé ----------
st.markdown("---")
st.caption("Feito por Rafael Nobre • Código no GitHub (adiciona o link do repositório aqui)")
