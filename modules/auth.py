import streamlit as st
import secrets
import time

# نخزن التوكنات المولدة في session_state
if "TOKENS" not in st.session_state:
    st.session_state.TOKENS = {}

def make_short_token(company: str, hours_valid: int = 4) -> str:
    """Generate short random token and save it in session with metadata"""
    token = secrets.token_urlsafe(6)  # ~8 chars
    st.session_state.TOKENS[token] = {
        "role": "editor",
        "company": company,
        "exp": time.time() + hours_valid * 3600,
    }
    return token

def verify_short_token(token: str) -> dict | None:
    """Check if token exists and not expired"""
    data = st.session_state.TOKENS.get(token)
    if not data:
        return None
    if time.time() > data["exp"]:
        # لو التوكن انتهى نشيله
        st.session_state.TOKENS.pop(token, None)
        return None
    return data

def get_admin_creds():
    user = st.secrets.get("ADMIN_USER", "admin")
    hash_hex = st.secrets.get("ADMIN_PASSWORD_HASH", "")
    return user, hash_hex

def sha256_hex(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()

def check_admin_password(password: str) -> bool:
    _, hash_hex = get_admin_creds()
    if not hash_hex:
        return False
    return sha256_hex(password) == hash_hex
