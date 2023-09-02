import os

from django.contrib.auth.tokens import default_token_generator
from djoser import utils
from djoser.conf import settings
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient, APITestCase

from app_users.email import PasswordResetEmail
from app_users.models import CustomUser
from app_users.serializers import UserSetPasswordSerializer

load_dotenv()


class UserCreationTestCase(APITestCase):
    """Регистрация пользователя"""

    def setUp(self):
        self.register_url = "/api/users/"
        self.valid_user_data = {
            "email": "ivan@mail.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "password": "qwerty123!",
            "phone": "+7(912)345-67-89",
        }
        self.invalid_phone_user_data = self.valid_user_data.copy()
        self.invalid_phone_user_data["phone"] = "89213456789"

        self.invalid_password_user_data = self.valid_user_data.copy()
        self.invalid_password_user_data["password"] = "qazwsxedcrfv"

    def test_user_can_register(self):
        """Валидные данные"""
        response = self.client.post(
            self.register_url, self.valid_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()
        self.assertEqual(response_data.get("email"), self.valid_user_data.get("email"))
        self.assertEqual(
            response_data.get("first_name"), self.valid_user_data.get("first_name")
        )
        self.assertEqual(
            response_data.get("last_name"), self.valid_user_data.get("last_name")
        )
        self.assertEqual(response_data.get("phone"), self.valid_user_data.get("phone"))
        self.assertEqual(response_data.get("image"), self.valid_user_data.get("image"))

        self.assertIsNone(response_data.get("password"))

        self.assertEqual(CustomUser.objects.count(), 1)

    def test_invalid_phone_number(self):
        """Некорректный номер телефона"""
        response = self.client.post(
            self.register_url, self.invalid_phone_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("phone", response.data)

        self.assertEqual(CustomUser.objects.count(), 0)

    def test_invalid_password(self):
        """Некорректный пароль"""
        response = self.client.post(
            self.register_url, self.invalid_password_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("password", response.data)

        self.assertEqual(CustomUser.objects.count(), 0)


class UserDisplayTestCase(APITestCase):
    """Чтение данных пользователя"""

    def setUp(self):
        self.url = "/api/users/"
        self.user_data = {
            "email": "ivan@mail.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "password": "qwerty123!",
            "phone": "+7(912)345-67-89",
        }

    def test_user_display(self):
        self.client.post(self.url, self.user_data, format="json")

        client = APIClient()
        login = client.post(
            "/api/token/", {"email": "ivan@mail.com", "password": "qwerty123!"}
        )
        access_token = login.json().get("access")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json().get("results")[0]

        self.assertEqual(response_data.get("email"), self.user_data["email"])
        self.assertEqual(response_data.get("first_name"), self.user_data["first_name"])
        self.assertEqual(response_data.get("last_name"), self.user_data["last_name"])
        self.assertEqual(response_data.get("phone"), self.user_data["phone"])
        self.assertIsNone(response_data.get("image"))


class TestPasswordResetEmail(APITestCase):
    """Отправка кастомного email"""

    def test_get_context_data(self):
        user = CustomUser(email="test@test.com")
        email = PasswordResetEmail()
        email.context = {"user": user}

        context = email.get_context_data()

        self.assertEqual(context["uid"], utils.encode_uid(user.pk))
        self.assertEqual(context["token"], default_token_generator.make_token(user))
        self.assertEqual(
            context["url"], settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        )
        self.assertEqual(context["domain"], os.getenv("HOST") + ":3000")
        self.assertEqual(context["protocol"], "http")
        self.assertEqual(context["site_name"], "ADS_ONLINE")


class UserSetPasswordSerializerTest(APITestCase):
    """Кастомный валидатор для установки нового пароля"""

    def test_valid_password(self):
        """Корректные пароли"""
        serializer = UserSetPasswordSerializer(
            data={
                "new_password": "Password123",
                "re_new_password": "Password123",
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_password_without_digit(self):
        """Пароли без цифр"""
        serializer = UserSetPasswordSerializer(
            data={
                "new_password": "Password",
                "re_new_password": "Password",
            }
        )
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_password_without_letter(self):
        """Пароли без букв"""
        serializer = UserSetPasswordSerializer(
            data={
                "new_password": "123456",
                "re_new_password": "123456",
            }
        )
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
