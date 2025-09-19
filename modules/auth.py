import streamlit as st
import secrets
import time
import hashlib

def _tokens_dict() -> dict:
    # ensure the dict exists and always use dict-style access
    return st.session_state.setdefault("TOKENS", {})

def make_short_token(company: str, hours_valid: int = 4) -> str:
    """Generate a short random token and store its metadata in session_state."""
    token = secrets.token_urlsafe(6)  # ~8 chars
    tokens = _tokens_dict()
    tokens[token] = {
        "role": "editor",
        "company": company,
        "exp": time.time() + hours_valid * 3600,
    }
    # write back explicitly (defensive)
    st.session_state["TOKENS"] = tokens
    return token

def verify_short_token(token: str) -> dict | None:
    """Return token metadata if valid; otherwise None."""
    tokens = _tokens_dict()
    data = tokens.get(token)
    if not data:
        return None
    if time.time() > data.get("exp", 0):
        # expire and remove
        tokens.pop(token, None)
        st.session_state["TOKENS"] = tokens
        return None
    return data

def get_admin_creds():
    user = st.secrets.get("ADMIN_USER", "admin")
    hash_hex = st.secrets.get("ADMIN_PASSWORD_HASH", "")
    return user, hash_hex

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def check_admin_password(password: str) -> bool:
    _, hash_hex = get_admin_creds()
    if not hash_hex:
        return False
    return sha256_hex(password) == hash_hex
