# src/load_data.py
import os
import sqlite3
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv

# SQLAlchemy é opcional. Se existir, usamos; senão, seguimos com sqlite3.
try:
    from sqlalchemy import create_engine  # type: ignore
    HAVE_SA = True
except Exception:
    HAVE_SA = False


def _read_config():
    load_dotenv(override=True)
    data_source = os.getenv("DATA_SOURCE", "sqlite").strip().lower()
    db_uri = os.getenv("DB_URI", "sqlite:///db/app.db").strip()
    csv_path = os.getenv("CSV_PATH", "data/sales.csv").strip()
    return data_source, db_uri, csv_path


def _sqlite_path_from_uri(db_uri: str) -> str:
    """Converte 'sqlite:///db/app.db' → 'db/app.db'. Aceita também caminhos diretos como 'db/app.db'."""
    if db_uri.startswith("sqlite:///"):
        parsed = urlparse(db_uri)
        path = parsed.path[1:] if parsed.path.startswith("/") else parsed.path
        return path
    return db_uri


def _load_sqlite(db_uri: str) -> pd.DataFrame:
    """Lê a tabela 'sales' de SQLite. Usa SQLAlchemy se existir, senão sqlite3 puro."""
    query = """
        SELECT id, date, customer, product, category,
               quantity, unit_price, total, region, channel
        FROM sales
    """
    if HAVE_SA:
        try:
            engine = create_engine(db_uri)
            return pd.read_sql(query, con=engine)
        except Exception:
            pass  # fallback

    db_path = _sqlite_path_from_uri(db_uri)
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base de dados não encontrada em '{db_path}'.")
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)


def _load_csv(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV não encontrado em '{csv_path}'. Ajusta CSV_PATH no .env ou cria o ficheiro."
        )
    return pd.read_csv(csv_path)


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza/preparação base: normalização, datas, numéricos, coluna month."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    required = [
        "id", "date", "customer", "product", "category",
        "quantity", "unit_price", "total", "region", "channel"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltam colunas no dataset: {missing}")

    # datas
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # numéricos
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)

    # total (recalcular onde faltar/NaN)
    if "total" not in df or df["total"].isna().all():
        df["total"] = df["quantity"] * df["unit_price"]
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce")
        mask = df["total"].isna()
        df.loc[mask, "total"] = df.loc[mask, "quantity"] * df.loc[mask, "unit_price"]

    # coluna mensal (1º dia do mês) para agregações
    df["month"] = df["date"].values.astype("datetime64[M]")

    # strings limpas
    for c in ["customer", "product", "category", "region", "channel"]:
        df[c] = df[c].astype(str).str.strip()

    return df


def load_sales() -> pd.DataFrame:
    """Carrega vendas conforme o .env (DATA_SOURCE=sqlite|csv)."""
    data_source, db_uri, csv_path = _read_config()
    if data_source == "sqlite":
        df = _load_sqlite(db_uri)
    elif data_source == "csv":
        df = _load_csv(csv_path)
    else:
        raise ValueError("DATA_SOURCE inválido. Usa 'sqlite' ou 'csv'.")
    return _prepare(df)


def get_filter_options(df: pd.DataFrame):
    """Retorna opções para filtros (datas, categorias, regiões, canais)."""
    if df.empty:
        return {"date_min": None, "date_max": None, "categories": [], "regions": [], "channels": []}
    return {
        "date_min": df["date"].min().date(),
        "date_max": df["date"].max().date(),
        "categories": sorted(df["category"].dropna().unique().tolist()),
        "regions": sorted(df["region"].dropna().unique().tolist()),
        "channels": sorted(df["channel"].dropna().unique().tolist()),
    }


if __name__ == "__main__":
    # Teste rápido
    try:
        sales = load_sales()
        opts = get_filter_options(sales)
        print("Linhas:", len(sales))
        print("Período:", opts["date_min"], "->", opts["date_max"])
        print("Categorias (ex.):", opts["categories"][:5])
    except Exception as e:
        print("Erro ao carregar dados:", e)
