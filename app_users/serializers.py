from typing import Any, Dict

from rest_framework import serializers

from .models import CustomUser
from .validators import PasswordValidator, PhoneValidator


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
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, default="user")

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

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "image", "id", "email"]
        read_only_fields = ["id", "email"]


class UserSetPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для установки нового пароля.
    """

    new_password = serializers.CharField(write_only=True)
    re_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация атрибутов.
        Проверяет, что новый пароль содержит хотя бы одну цифру и одну букву.

        :param attrs: Словарь атрибутов для валидации.
        :return: Валидированный словарь атрибутов.
        :raises serializers.ValidationError: если пароль не соответствует требованиям.
        """
        password = attrs.get("new_password")

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну цифру."
            )
        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну букву."
            )

        return super().validate(attrs)
