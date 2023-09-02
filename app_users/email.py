import os
from typing import Any, Dict

from django.contrib.auth.tokens import default_token_generator
from djoser import utils
from djoser.conf import settings
from dotenv import load_dotenv
from templated_mail.mail import BaseEmailMessage

load_dotenv()


class PasswordResetEmail(BaseEmailMessage):
    """
    Пользовательский класс электронного письма для сброса пароля.
    Наследует от BaseEmailMessage для использования его возможностей отправки писем
    и настраивает контекстные данные письма.

    :return: Словарь с контекстными данными для электронного письма.
    """

    template_name = "email/password_reset.html"

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        context["domain"] = os.getenv("HOST") + ":3000"
        context["protocol"] = "http"
        context["site_name"] = "ADS_ONLINE"
        return context
