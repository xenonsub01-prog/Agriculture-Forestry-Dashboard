import streamlit as st
import pandas as pd
from datetime import datetime
from modules import auth
from modules.data import load_master, update_row
from modules.ui import header, filter_panel, kpi_row
from modules.export import to_excel_bytes, to_pdf_bytes

st.set_page_config(page_title="Warehouse Orders Demo", layout="wide")

COMPANY = "Agriculture & Forestry"

# ------------------------ Session Initialization -------------------------
if "role" not in st.session_state:
    st.session_state.role = None
if "company" not in st.session_state:
    st.session_state.company = COMPANY
if "username" not in st.session_state:
    st.session_state.username = ""
if "df" not in st.session_state:
    st.session_state.df = load_master()
if "log" not in st.session_state:
    st.session_state.log = []  # each: {ts,user,order,from,to}

# ------------------------ Auth / Routing ---------------------------------
def show_login():
    st.title("Warehouse Orders Demo")
    header(COMPANY)
    st.subheader("Sign In")
    tab_admin, tab_token = st.tabs(["Admin (password)", "Editor (token link)"])

    with tab_admin:
        user = st.text_input("Username", value="")
        pwd = st.text_input("Password", value="", type="password")
        if st.button("Sign in as Admin", type="primary"):
            admin_user, _ = auth.get_admin_creds()
            if user == admin_user and auth.check_admin_password(pwd):
                st.session_state.role = "admin"
                st.session_state.username = user
                st.success("Signed in as Admin.")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab_token:
        token = st.text_input("Paste token from link", placeholder="e.g. Ab3x7DzQ")
        if st.button("Continue as Editor", type="primary"):
            data = auth.verify_short_token(token)
            if data and data.get("role") == "editor":
                st.session_state.role = "editor"
                st.session_state.username = "Client"
                st.session_state.company = data.get("company", COMPANY)
                st.success("Editor access granted.")
                st.rerun()
            else:
                st.error("Invalid or expired token.")

def nav():
    if st.session_state.role == "admin":
        return st.sidebar.radio("Navigation", ["Dashboard", "Master", "VIC", "NSW", "SA", "Log", "FAQ", "Admin"])
    elif st.session_state.role == "editor":
        return st.sidebar.radio("Navigation", ["Dashboard", "Master", "VIC", "NSW", "SA", "Log", "FAQ"])
    return None

def ensure_editor():
    if st.session_state.role not in ("admin", "editor"):
        st.stop()

# ------------------------ Pages ------------------------------------------
def page_dashboard():
    ensure_editor()
    header(st.session_state.company)
    df = st.session_state.df
    df_f = filter_panel(df)
    kpi_row(df_f)
    st.dataframe(df_f, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Export to Excel",
            to_excel_bytes(df_f),
            file_name="orders.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with c2:
        st.download_button(
            "Export to PDF",
            to_pdf_bytes(df_f, st.session_state.company),
            file_name="orders.pdf",
            mime="application/pdf",
        )

def edit_view(warehouse: str | None):
    ensure_editor()
    header(st.session_state.company)
    df = st.session_state.df
    if warehouse:
        df = df[df["Warehouse"] == warehouse]
    df_f = filter_panel(df)
    kpi_row(df_f)

    st.write("Select a row to update status and invoice:")
    row = st.selectbox("Order", options=[""] + df_f["OrderID"].tolist(), index=0)
    if row:
        current = st.session_state.df[st.session_state.df["OrderID"] == row].iloc[0]
        col1, col2, col3 = st.columns(3)
        new_status = col1.selectbox(
            "New Status",
            ["New", "In Progress", "On Hold", "Completed", "Invoiced"],
            index=["New","In Progress","On Hold","Completed","Invoiced"].index(current["Status"]),
        )
        new_invoice = col2.text_input("Invoice No.", value=current["InvoiceNo"] if current["InvoiceNo"] else "")
        col3.write("")
        if col3.button("Update", type="primary"):
            st.session_state.df, old_status = update_row(
                st.session_state.df, row, new_status, new_invoice, st.session_state.username or "User"
            )
            st.session_state.log.append({
                "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "User": st.session_state.username or "User",
                "OrderID": row,
                "From→To": f"{old_status}→{new_status}",
            })
            st.success(f"Order {row} updated.")
            st.rerun()

    st.dataframe(df_f, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Export to Excel",
            to_excel_bytes(df_f),
            file_name=f"{warehouse or 'master'}_orders.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with c2:
        st.download_button(
            "Export to PDF",
            to_pdf_bytes(df_f, st.session_state.company),
            file_name=f"{warehouse or 'master'}_orders.pdf",
            mime="application/pdf",
        )

def page_log():
    ensure_editor()
    header(st.session_state.company)
    st.subheader("Change Log")
    if st.session_state.log:
        st.dataframe(pd.DataFrame(st.session_state.log), use_container_width=True, hide_index=True)
    else:
        st.info("No changes yet in this session.")

def page_admin():
    if st.session_state.role != "admin":
        st.stop()
    header(st.session_state.company)
    st.subheader("Admin")
    st.caption("Create a temporary short Editor token (easy to share).")

    col1, col2 = st.columns(2)
    company = col1.text_input("Company on reports", value=st.session_state.company)
    hours = col2.number_input("Hours Valid", min_value=1, max_value=72, value=4, step=1)
    if st.button("Generate Token", type="primary"):
        token = auth.make_short_token(company, int(hours))
        app_url = "https://agriculture-forestry-dashboard-uzu2pyhyl4jnf2xbjazlaf.streamlit.app"
        full_link = f"{app_url}/?token={token}"
        st.code(full_link, language="text")
        st.success("Share this link with the client.")

    st.divider()
    if st.button("Reset Demo (this session)"):
        st.session_state.df = load_master()
        st.session_state.log = []
        st.success("Session reset.")

def page_faq():
    ensure_editor()
    header(st.session_state.company)
    st.subheader("FAQ")
    qa = [
        ("How do I filter orders?", "Use the Filters panel at the top of each page."),
        ("How do I update a status or invoice?", "Open any warehouse tab, select an Order and update."),
        ("Where can I see KPIs?", "KPIs appear above every table."),
        ("Can I export the view?", "Yes, use the Export buttons."),
        ("What happens to my edits?", "This is a demo, edits reset after session ends."),
        ("Can multiple managers use it?", "Yes, each session is isolated."),
        ("What statuses exist?", "New, In Progress, On Hold, Completed, and Invoiced."),
        ("Do you log changes?", "Yes, the Log page lists changes for this session."),
        ("How do I access as Editor?", "The admin generates a short token link."),
        ("Can this integrate with MYOB EXO?", "Yes, can be extended in production."),
    ]
    for i, (q, a) in enumerate(qa, 1):
        with st.expander(f"{i}. {q}"):
            st.write(a)

# ------------------------ URL Token Auto-Login ---------------------------
query_params = st.query_params
if "token" in query_params and not st.session_state.role:
    data = auth.verify_short_token(query_params["token"])
    if data and data.get("role") == "editor":
        st.session_state.role = "editor"
        st.session_state.username = "Client"
        st.session_state.company = data.get("company", COMPANY)

# ------------------------ App Entry --------------------------------------
if not st.session_state.role:
    show_login()
else:
    page = nav()
    if page == "Dashboard":
        page_dashboard()
    elif page == "Master":
        edit_view(None)
    elif page == "VIC":
        edit_view("VIC")
    elif page == "NSW":
        edit_view("NSW")
    elif page == "SA":
        edit_view("SA")
    elif page == "Log":
        page_log()
    elif page == "Admin":
        page_admin()
    elif page == "FAQ":
        page_faq()
