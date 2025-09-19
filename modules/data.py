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
    # Parse due dates and last updates
    due = pd.to_datetime(df["DueDate"], errors="coerce").dt.date
    last_upd = pd.to_datetime(df["LastUpdatedOn"], errors="coerce")

    # Today and start of week (Monday)
    now_ts = pd.Timestamp.now().normalize()
    start_week = now_ts - pd.Timedelta(days=now_ts.weekday())

    open_mask = df["Status"].isin(["New", "In Progress", "On Hold"])
    due_today_mask = (due == pd.Timestamp.now().date())
    overdue_mask = (due < pd.Timestamp.now().date())
    invoiced_this_week_mask = (df["Status"] == "Invoiced") & (last_upd >= start_week)

    return {
        "Open": int(open_mask.sum()),
        "Due Today": int(due_today_mask.sum()),
        "Overdue": int(overdue_mask.sum()),
        "Invoiced This Week": int(invoiced_this_week_mask.sum()),
    }
