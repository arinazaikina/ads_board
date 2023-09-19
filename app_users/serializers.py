from typing import Any, Dict

from djoser.serializers import PasswordResetConfirmSerializer
from rest_framework import serializers

from app_ads.validators import NotEmptyStringValidator
from .models import CustomUser
from .validators import PasswordValidator, PhoneValidator, EmailValidator


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Настроена проверка номера телефона.
    Телефонный номер должен быть в формате: +7(9**)***-**-**
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[PasswordValidator()]
    )
    phone = serializers.CharField(validators=[PhoneValidator()])
    role = serializers.ChoiceField(
        choices=CustomUser.ROLE_CHOICES, default="user", read_only=True
    )
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = CustomUser
        fields = ["id", "email", "password", "first_name", "last_name", "phone", "role"]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Создает новый экземпляр модели CustomUser с переданными данными.
        Устанавливает пароль пользователя.
        Сохраняет пользователя в базе данных.

        :param validated_data: Валидированные данные сериализатора.
        """
        user = CustomUser.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            role=validated_data.get("role", "user"),
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CustomUser, представляющей пользователей.
    """

    phone = serializers.CharField(validators=[PhoneValidator()])
    first_name = serializers.CharField(validators=[NotEmptyStringValidator()])
    last_name = serializers.CharField(validators=[NotEmptyStringValidator()])

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "image", "id", "email"]
        read_only_fields = ["id", "email"]


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """
    Сериализатор для подтверждения установки нового пароля.
    """

    re_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация атрибутов.
        Проверяет, что новый пароль содержит хотя бы одну цифру и одну букву.

        :param attrs: Словарь атрибутов для валидации.
        :return: Валидированный словарь атрибутов.
        :raises serializers.ValidationError: Если пароль не соответствует требованиям.
        """
        attrs = super().validate(attrs)
        new_password = attrs.get("new_password")
        re_new_password = attrs.get("re_new_password")

        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError(
                {"new_password": "Пароль должен содержать хотя бы одну цифру."}
            )
        if not any(char.isalpha() for char in new_password):
            raise serializers.ValidationError(
                {"new_password": "Пароль должен содержать хотя бы одну букву."}
            )

        if new_password != re_new_password:
            raise serializers.ValidationError(
                {"re_new_password": "Пароли не совпадают."}
            )

        return attrs


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def validate_email(value):
        """
        Проверяет, существует ли введенный адрес электронной почты в базе данных.
        """
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Данный адрес электронной почты не найден.")
        return value
