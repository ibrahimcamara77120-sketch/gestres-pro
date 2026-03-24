import pytest
from src.utils.security import (
    hash_password, verify_password, generate_token, hash_token,
    generate_session_expiry, validate_password_strength,
    validate_email, validate_siret, sanitize_input
)


class TestPasswordHashing:

    def test_hash_different_from_plaintext(self):
        hashed = hash_password("SecurePass123!")
        assert hashed != "SecurePass123!"

    def test_hash_bcrypt_prefix(self):
        hashed = hash_password("SecurePass123!")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("SecurePass123!", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_different_hashes(self):
        # bcrypt génère un salt différent à chaque fois
        h1 = hash_password("SecurePass123!")
        h2 = hash_password("SecurePass123!")
        assert h1 != h2
        assert verify_password("SecurePass123!", h1) is True
        assert verify_password("SecurePass123!", h2) is True

    def test_empty_string_hash(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notEmpty", hashed) is False

    def test_unicode_password(self):
        pwd = "Pässwörd123!"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True
        assert verify_password("Passw0rd123!", hashed) is False

    def test_long_password(self):
        pwd = "A" * 20 + "a" * 20 + "1111!"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True


class TestTokenGeneration:

    def test_token_length(self):
        token = generate_token()
        assert len(token) == 64  # 32 bytes hex

    def test_tokens_are_unique(self):
        tokens = [generate_token() for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_token_is_hexadecimal(self):
        token = generate_token()
        int(token, 16)  # lève ValueError si non-hex

    def test_hash_token_deterministic(self):
        token = "test_token_123"
        assert hash_token(token) == hash_token(token)

    def test_hash_token_length(self):
        assert len(hash_token("anything")) == 64  # SHA-256

    def test_different_tokens_different_hashes(self):
        assert hash_token("token_a") != hash_token("token_b")

    def test_session_expiry_in_future(self):
        from datetime import datetime, timezone
        expiry = generate_session_expiry()
        assert expiry > datetime.now(timezone.utc)


class TestPasswordStrength:

    def test_valid_password(self):
        valid, errors = validate_password_strength("SecurePass123!")
        assert valid is True
        assert len(errors) == 0

    def test_too_short(self):
        valid, errors = validate_password_strength("Ab1!")
        assert valid is False
        assert any("caractères" in e for e in errors)

    def test_no_uppercase(self):
        valid, errors = validate_password_strength("securepass123!")
        assert valid is False
        assert any("majuscule" in e for e in errors)

    def test_no_lowercase(self):
        valid, errors = validate_password_strength("SECUREPASS123!")
        assert valid is False
        assert any("minuscule" in e for e in errors)

    def test_no_digit(self):
        valid, errors = validate_password_strength("SecurePass!!")
        assert valid is False
        assert any("chiffre" in e for e in errors)

    def test_no_special_char(self):
        valid, errors = validate_password_strength("SecurePass123")
        assert valid is False
        assert any("spécial" in e for e in errors)

    def test_multiple_errors_at_once(self):
        # mot de passe vide
        valid, errors = validate_password_strength("abc")
        assert valid is False
        assert len(errors) >= 3

    def test_exactly_8_chars(self):
        valid, errors = validate_password_strength("Abcde1@!")
        assert valid is True

    def test_special_chars_accepted(self):
        for char in "!@#$%^&*()":
            pwd = f"SecurePass1{char}"
            valid, _ = validate_password_strength(pwd)
            assert valid is True, f"Caractère {char} devrait être accepté"


class TestEmailValidation:

    def test_valid_emails(self):
        valides = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
            "a@b.fr",
        ]
        for email in valides:
            assert validate_email(email) is True, f"{email} devrait être valide"

    def test_invalid_emails(self):
        invalides = [
            "not_an_email",
            "@missing_local.com",
            "missing@.com",
            "spaces in@email.com",
            "missing_domain@",
            "double@@domain.com",
            "",
        ]
        for email in invalides:
            assert validate_email(email) is False, f"{email} devrait être invalide"

    def test_case_insensitive_domain(self):
        assert validate_email("test@EXAMPLE.COM") is True


class TestSiretValidation:

    def test_valid_siret(self):
        assert validate_siret("73282932000074") is True

    def test_empty_siret_optional(self):
        assert validate_siret("") is True
        assert validate_siret(None) is True

    def test_invalid_length_short(self):
        assert validate_siret("123456") is False

    def test_invalid_length_long(self):
        assert validate_siret("123456789012345") is False

    def test_invalid_characters(self):
        assert validate_siret("1234567890ABCD") is False

    def test_siret_with_spaces_stripped(self):
        assert validate_siret("732 829 320 00074") is True

    def test_invalid_checksum(self):
        # 14 chiffres mais checksum Luhn incorrect
        assert validate_siret("11111111111111") is False


class TestSanitizeInput:

    def test_strips_whitespace(self):
        assert sanitize_input("  test  ") == "test"

    def test_strips_tabs_and_newlines_around(self):
        assert sanitize_input("\n\ttest\n\t") == "test"

    def test_none_returns_none(self):
        assert sanitize_input(None) is None

    def test_empty_returns_none(self):
        assert sanitize_input("") is None

    def test_spaces_only_returns_none(self):
        assert sanitize_input("   ") is None

    def test_preserves_internal_newlines(self):
        result = sanitize_input("line1\nline2")
        assert "line1" in result
        assert "line2" in result

    def test_removes_control_characters(self):
        result = sanitize_input("test\x00\x01\x02normal")
        assert "\x00" not in result
        assert "test" in result
        assert "normal" in result

    def test_normal_text_unchanged(self):
        assert sanitize_input("Hello World") == "Hello World"

    def test_numbers_unchanged(self):
        assert sanitize_input("12345") == "12345"
