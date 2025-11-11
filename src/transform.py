# src/transform.py
from typing import Iterable, Optional, Tuple
import pandas as pd
from load_data import load_sales


# ---------- Filtros ----------
def apply_filters(
    df: pd.DataFrame,
    date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
    categories: Optional[Iterable[str]] = None,
    regions: Optional[Iterable[str]] = None,
    channels: Optional[Iterable[str]] = None,
    search_customer: Optional[str] = None,
) -> pd.DataFrame:
    out = df.copy()

    if date_range is not None:
        start, end = date_range
        out = out[(out["date"] >= pd.to_datetime(start)) & (out["date"] <= pd.to_datetime(end))]

    if categories:
        out = out[out["category"].isin(list(categories))]

    if regions:
        out = out[out["region"].isin(list(regions))]

    if channels:
        out = out[out["channel"].isin(list(channels))]

    if search_customer:
        q = str(search_customer).strip().lower()
        if q:
            out = out[out["customer"].str.lower().str.contains(q, na=False)]

    return out.reset_index(drop=True)


# ---------- KPIs ----------
def calc_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0.0, "num_vendas": 0, "ticket_medio": 0.0}
    total = float(df["total"].sum())
    num_vendas = int(len(df))
    ticket_medio = total / num_vendas if num_vendas else 0.0
    return {
        "total": round(total, 2),
        "num_vendas": num_vendas,
        "ticket_medio": round(ticket_medio, 2),
    }


# ---------- Agregações ----------
def vendas_mensais(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["month", "faturacao"])
    out = df.groupby("month", as_index=False)["total"].sum()
    out = out.rename(columns={"total": "faturacao"})
    return out.sort_values("month")


def top_produtos(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["product", "faturacao"])
    out = df.groupby("product", as_index=False)["total"].sum()
    out = out.rename(columns={"total": "faturacao"})
    return out.sort_values("faturacao", ascending=False).head(n)


def distribuicao_canal(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["channel", "faturacao"])
    out = df.groupby("channel", as_index=False)["total"].sum()
    return out.rename(columns={"total": "faturacao"})


def distribuicao_regiao(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["region", "faturacao"])
    out = df.groupby("region", as_index=False)["total"].sum()
    return out.rename(columns={"total": "faturacao"})


# ---------- Teste rápido ----------
if __name__ == "__main__":
    sales = load_sales()
    print("Linhas totais:", len(sales))

    # Sem filtros
    kpis = calc_kpis(sales)
    print("KPIs (sem filtros):", kpis)

    print("\nMensal:")
    print(vendas_mensais(sales))

    print("\nTop produtos:")
    print(top_produtos(sales, n=5))

    print("\nPor canal:")
    print(distribuicao_canal(sales))

    print("\nPor região:")
    print(distribuicao_regiao(sales))

    # Exemplo com filtros (Janeiro a Março de 2023, categoria 'Periféricos')
    f = apply_filters(
        sales,
        date_range=("2023-01-01", "2023-03-31"),
        categories=["Periféricos"],
    )
    print("\nCom filtros (2023-01 a 2023-03, Periféricos):")
    print("Linhas filtradas:", len(f))
    print("KPIs filtrados:", calc_kpis(f))
