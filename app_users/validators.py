import re

from django.core.exceptions import ValidationError


class PhoneValidator:
    """
    Проверяет, соответствует ли номер телефона формату '+7(***)***-**-**'
    """

    phone_regex = r"^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$"
    message = "Телефонный номер должен быть в формате: +7(***)***-**-**"

    def __call__(self, value: str):
        if not re.match(self.phone_regex, value):
            raise ValidationError(message=self.message)


class PasswordValidator:
    """
    Проверяет, содержит ли пароль и буквы, и цифры.
    """

    def __call__(self, value: str):
        if len(value) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру.")
        if not any(char.isalpha() for char in value):
            raise ValidationError("Пароль должен содержать хотя бы одну букву.")
