from rest_framework import serializers


class NotEmptyStringValidator:
    """
    Проверяет, что значение не является пустой строкой
    или строкой, состоящей только из пробелов.

    При попытке сохранить пустое значение или значение, состоящее только из пробелов,
    будет вызвано исключение serializers.ValidationError.
    """

    def __call__(self, value: str):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError(
                "Поле не должно быть пустым или состоять только из пробелов."
            )
