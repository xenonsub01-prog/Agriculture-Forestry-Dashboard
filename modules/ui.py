
import streamlit as st
import pandas as pd
from modules.data import filter_df, kpis

def header(company: str):
    st.markdown(f"""
    <div style="padding:12px 16px;border-radius:16px;background:#0E1117;color:white;margin-bottom:8px;">
      <h2 style="margin:0;">Welcome {company}</h2>
      <p style="margin:4px 0 0 0;opacity:.8;">Live Warehouse Order Dashboard (Demo)</p>
    </div>
    """, unsafe_allow_html=True)

def filter_panel(df: pd.DataFrame):
    with st.expander("Filters", expanded=True):
        cols = st.columns(5)
        warehouse = cols[0].multiselect("Warehouse", sorted(df["Warehouse"].unique().tolist()))
        status = cols[1].multiselect("Status", sorted(df["Status"].unique().tolist()))
        priority = cols[2].multiselect("Priority", sorted(df["Priority"].unique().tolist()))
        date_from = cols[3].date_input("Due Date From", value=None)
        date_to = cols[4].date_input("Due Date To", value=None)
        search = st.text_input("Search")
        df_f = filter_df(
            df,
            warehouse=warehouse or None,
            status=status or None,
            priority=priority or None,
            search=search,
            date_from=date_from.isoformat() if date_from else "",
            date_to=date_to.isoformat() if date_to else "",
        )
    return df_f

def kpi_row(df: pd.DataFrame):
    m = kpis(df)
    a,b,c,d = st.columns(4)
    a.metric("Open", m["Open"])
    b.metric("Due Today", m["Due Today"])
    c.metric("Overdue", m["Overdue"])
    d.metric("Invoiced This Week", m["Invoiced This Week"])
