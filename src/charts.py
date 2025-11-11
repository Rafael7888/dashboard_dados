# src/charts.py
import plotly.express as px
import pandas as pd


def chart_vendas_mensais(df: pd.DataFrame):
    """Gráfico de linha: evolução da faturação mensal."""
    if df.empty:
        return px.line(title="Sem dados")
    fig = px.line(
        df,
        x="month",
        y="faturacao",
        markers=True,
        title="Evolução Mensal da Faturação",
    )
    fig.update_layout(xaxis_title="Mês", yaxis_title="Faturação (€)")
    return fig


def chart_top_produtos(df: pd.DataFrame):
    """Gráfico de barras: top produtos por faturação."""
    if df.empty:
        return px.bar(title="Sem dados")
    fig = px.bar(
        df,
        x="product",
        y="faturacao",
        title="Top Produtos por Faturação",
        text="faturacao",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(xaxis_title="Produto", yaxis_title="Faturação (€)")
    return fig


def chart_distribuicao(df: pd.DataFrame, col: str, titulo: str):
    """Gráfico de pizza genérico (canal ou região)."""
    if df.empty:
        return px.pie(title="Sem dados")
    fig = px.pie(
        df,
        names=col,
        values="faturacao",
        title=titulo,
        hole=0.4,  # gráfico donut
    )
    return fig


# ---------- Teste rápido ----------
if __name__ == "__main__":
    import sys
    from load_data import load_sales
    from transform import vendas_mensais, top_produtos, distribuicao_canal

    sales = load_sales()
    print("Linhas carregadas:", len(sales))

    df_mensal = vendas_mensais(sales)
    df_top = top_produtos(sales, n=5)
    df_canal = distribuicao_canal(sales)

    # Teste offline: exporta HTML para ver no browser
    chart_vendas_mensais(df_mensal).write_html("mensal.html")
    chart_top_produtos(df_top).write_html("top_produtos.html")
    chart_distribuicao(df_canal, "channel", "Distribuição por Canal").write_html("canal.html")

    print("Gráficos gerados: mensal.html, top_produtos.html, canal.html")
