
import pandas as pd
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "master_orders.csv"

def load_master() -> pd.DataFrame:
    # Always load a fresh copy from disk for this session
    return pd.read_csv(DATA_PATH, dtype=str).fillna("")

def update_row(df: pd.DataFrame, order_id: str, new_status: str, new_invoice: str, user: str) -> pd.DataFrame:
    idx = df.index[df["OrderID"] == order_id]
    if len(idx) == 0:
        return df
    i = idx[0]
    old_status = df.at[i, "Status"]
    df.at[i, "Status"] = new_status
    df.at[i, "InvoiceNo"] = new_invoice
    df.at[i, "UpdatedBy"] = user
    df.at[i, "LastUpdatedOn"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df, old_status

def filter_df(df: pd.DataFrame, warehouse: list[str] | None = None, status: list[str] | None = None,
              priority: list[str] | None = None, search: str = "", date_from: str = "", date_to: str = "") -> pd.DataFrame:
    out = df.copy()
    if warehouse:
        out = out[out["Warehouse"].isin(warehouse)]
    if status:
        out = out[out["Status"].isin(status)]
    if priority:
        out = out[out["Priority"].isin(priority)]
    if search:
        s = search.strip().lower()
        out = out[out.apply(lambda r: s in (" ".join(map(str, r.values))).lower(), axis=1)]
    if date_from:
        out = out[out["DueDate"] >= date_from]
    if date_to:
        out = out[out["DueDate"] <= date_to]
    return out

def kpis(df: pd.DataFrame) -> dict:
    from datetime import date, timedelta, datetime
    today = date.today().isoformat()
    # Invoices this week
    d = pd.to_datetime(df["LastUpdatedOn"], errors="coerce")
    this_week = (d.dt.date >= (datetime.today().date() - pd.to_timedelta(d.dt.weekday, unit="D")))
    invoiced_this_week = int(((df["Status"] == "Invoiced") & this_week.fillna(False)).sum())
    return {
        "Open": int((df["Status"].isin(["New", "In Progress", "On Hold"])).sum()),
        "Due Today": int((df["DueDate"] == today).sum()),
        "Overdue": int((df["DueDate"] < today).sum()),
        "Invoiced This Week": invoiced_this_week,
    }
