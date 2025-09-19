import os, time, hmac, hashlib, base64, json
from datetime import datetime, timedelta
import streamlit as st

def get_secret():
    return str(st.secrets.get("APP_SECRET", "dev_secret_change_me"))

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def ub64url(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def sign(payload: dict) -> str:
    secret = get_secret().encode()
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(secret, body, hashlib.sha256).digest()
    return b64url(body) + "." + b64url(sig)

def verify(token: str) -> dict | None:
    try:
        body_b64, sig_b64 = token.split(".")
        body = ub64url(body_b64)
        expected_sig = ub64url(sig_b64)
        secret = get_secret().encode()
        actual_sig = hmac.new(secret, body, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        data = json.loads(body.decode())
        if "exp" in data and time.time() > data["exp"]:
            return None
        return data
    except Exception:
        return None

def make_editor_token(company: str, hours_valid: int = 4) -> str:
    payload = {
        "role": "editor",
        "company": company,
        "exp": int(time.time() + hours_valid * 3600),
        "iat": int(time.time()),
    }
    return sign(payload)

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
