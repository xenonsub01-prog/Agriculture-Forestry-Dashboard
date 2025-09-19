import streamlit as st
import secrets
import time
import hashlib


# A single shared dict across all sessions on the same server process
@st.cache_resource
def _tokens_store() -> dict:
    # { token: {"role": "...", "company": "...", "exp": <unix_ts>} }
    return {}


def make_short_token(company: str, hours_valid: int = 4) -> str:
    """
    Generate a short random token and store its metadata
    in a shared cache so other sessions (client link) can see it.
    """
    token = secrets.token_urlsafe(6)  # ~8 chars URL-safe
    store = _tokens_store()
    store[token] = {
        "role": "editor",
        "company": company,
        "exp": time.time() + hours_valid * 3600,
    }
    return token


def verify_short_token(token: str) -> dict | None:
    """Return token metadata if valid; otherwise None (and remove if expired)."""
    store = _tokens_store()
    data = store.get(token)
    if not data:
        return None
    if time.time() > data.get("exp", 0):
        # remove expired
        try:
            del store[token]
        except KeyError:
            pass
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
