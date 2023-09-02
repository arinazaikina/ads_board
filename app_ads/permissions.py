from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrOwner(BasePermission):
    """
    Пользовательское разрешение, проверяющее права доступа на основе роли и владения объектом.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет, имеет ли пользователь общие права доступа.
        :param request: HTTP-запрос.
        :param view: Объект APIView.
        :return: True, если пользователь аутентифицирован, иначе False.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Проверяет, имеет ли пользователь права доступа к конкретному объекту.
        :param request: HTTP-запрос.
        :param view: Объект APIView.
        :param obj: Объект, к которому идет запрос.
        :return: True, если пользователь имеет права доступа, иначе False.
        """
        if request.user.role == "admin":
            return True

        if hasattr(obj, "author"):
            if obj.author == request.user:
                return True
        return False
