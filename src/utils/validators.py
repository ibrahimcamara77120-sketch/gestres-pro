from typing import Any
import re


class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_required(value: Any, field_name: str) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(field_name, "Ce champ est obligatoire")


def validate_length(value: str | None, field_name: str, min_length: int | None = None, max_length: int | None = None) -> None:
    if value is None:
        return

    length = len(value)

    if min_length is not None and length < min_length:
        raise ValidationError(field_name, f"Minimum {min_length} caractères")

    if max_length is not None and length > max_length:
        raise ValidationError(field_name, f"Maximum {max_length} caractères")


def validate_pattern(value: str | None, field_name: str, pattern: str, message: str) -> None:
    if value is None:
        return
    if not re.match(pattern, value):
        raise ValidationError(field_name, message)


def validate_email_format(email: str | None, field_name: str = "email") -> None:
    if email is None:
        return
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationError(field_name, "Format d'email invalide")


def validate_numeric(value: str | None, field_name: str) -> None:
    if value is None:
        return
    if not value.isdigit():
        raise ValidationError(field_name, "Doit être un nombre")


def validate_choice(value: Any, field_name: str, choices: list) -> None:
    if value is None:
        return
    if value not in choices:
        choices_str = ", ".join(str(c) for c in choices)
        raise ValidationError(field_name, f"Valeur invalide. Choix : {choices_str}")


class Validator:
    def __init__(self):
        self.errors: list[ValidationError] = []

    def add_error(self, field: str, message: str) -> None:
        self.errors.append(ValidationError(field, message))

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def get_errors(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for error in self.errors:
            if error.field not in result:
                result[error.field] = []
            result[error.field].append(error.message)
        return result

    def validate_required(self, value: Any, field_name: str) -> None:
        try:
            validate_required(value, field_name)
        except ValidationError as e:
            self.errors.append(e)

    def validate_length(self, value: str | None, field_name: str, min_length: int | None = None, max_length: int | None = None) -> None:
        try:
            validate_length(value, field_name, min_length, max_length)
        except ValidationError as e:
            self.errors.append(e)

    def validate_email(self, email: str | None, field_name: str = "email") -> None:
        try:
            validate_email_format(email, field_name)
        except ValidationError as e:
            self.errors.append(e)
