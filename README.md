
# Live Warehouse Order Dashboard (Demo)

A Streamlit demo that matches the Upwork brief: master order sheet, per-warehouse tabs (VIC/NSW/SA), editor status updates, real-time KPIs, change log, and PDF/Excel export. This demo is **non‑persistent**: any edits are temporary for the current session only and reset automatically when the session ends.

## Key Features
- Intro: **"Welcome Agriculture & Forestry"**
- Master sheet + VIC/NSW/SA tabs (50 rows per warehouse).
- Filters (Warehouse, Status, Priority, Date Range, Search).
- KPIs (Open, Due Today, Overdue, Invoiced This Week).
- Update status/invoice from any warehouse view.
- Auto log: DateTime / User / OrderID / From→To.
- UpdatedBy and LastUpdatedOn auto-populate.
- Export filtered data to **Excel** or **PDF** (header contains *Agriculture & Forestry*).
- FAQ page with 10 common questions and deep links.
- **Admin** can generate **temporary tokens** (signed URL) for an **Editor** to access the app without a password.

## Run Locally
```bash
# 1) Create virtualenv (recommended)
python -m venv .venv && . .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 2) Install
pip install -r requirements.txt

# 3) Add secrets
# Create .streamlit/secrets.toml with:
# ADMIN_USER="admin"
# ADMIN_PASSWORD_HASH="paste_bcrypt_or_sha256_hash_here"
# APP_SECRET="a_long_random_secret_string"

# For quick start you can use a SHA256 hash:
# python - <<'PY'
# import hashlib; print(hashlib.sha256("admin123".encode()).hexdigest())
# PY
# Then paste the printed hash into ADMIN_PASSWORD_HASH and use password "admin123".

# 4) Run
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push this folder to a public GitHub repo (e.g., **warehouse_order_demo**).
2. On Streamlit Cloud, set three secrets in **App settings → Secrets**:
   - `ADMIN_USER`
   - `ADMIN_PASSWORD_HASH`
   - `APP_SECRET`
3. Deploy. Use `/` base URL for the app.
4. As **Admin**, open the app, go to **Admin** page → **Generate Token**, set expiry (e.g., 4 hours), copy the generated link and send it to the client.
5. Client opens the link and gets **Editor** access. All edits are temporary to their session.

## Notes
- This is a demo; no database is used. Data loads from CSV and lives in memory.
- When the browser session ends, edits disappear.
- Tokens are stateless and signed with `APP_SECRET` (HMAC-SHA256) and include expiry.
