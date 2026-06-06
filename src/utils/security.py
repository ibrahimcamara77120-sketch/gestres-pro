import secrets
import hashlib
import re
from datetime import datetime, timedelta, timezone

import bcrypt

import config


def hash_password(password):
    salt = bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def generate_token():
    return secrets.token_hex(32)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_session_expiry():
    return datetime.now(timezone.utc) + timedelta(hours=config.SESSION_DURATION_HOURS)


def validate_password_strength(password):
    errors = []

    if len(password) < config.PASSWORD_MIN_LENGTH:
        errors.append(f"Minimum {config.PASSWORD_MIN_LENGTH} caractères requis")

    if not re.search(r"[A-Z]", password):
        errors.append("Au moins une majuscule requise")

    if not re.search(r"[a-z]", password):
        errors.append("Au moins une minuscule requise")

    if not re.search(r"\d", password):
        errors.append("Au moins un chiffre requis")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Au moins un caractère spécial requis")

    return len(errors) == 0, errors


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_siret(siret):
    if not siret:
        return True

    siret = siret.replace(" ", "")

    if not re.match(r"^\d{14}$", siret):
        return False

    if all(c == "0" for c in siret):
        return False

    # Luhn
    total = 0
    for i, digit in enumerate(siret):
        d = int(digit)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d

    return total % 10 == 0


def sanitize_input(text):
    if text is None:
        return None

    text = text.strip()
    text = "".join(char for char in text if char >= " " or char in "\n\t")

    return text if text else None
