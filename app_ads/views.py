from typing import List, Type

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from .filters import AdFilter
from .models import Ad, Review
from .permissions import IsAdminOrOwner
from .serializers import AdListSerializer, AdSerializer, ReviewSerializer


class AdPagination(pagination.PageNumberPagination):
    """
    Пагинация для объявлений.
    """

    page_size = 4
    page_query_param = "page"


class AdViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для работы с объявлениями.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = AdPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdFilter
    http_method_names = ["get", "post", "patch", "delete"]

    permissions = {
        "list": [AllowAny()],
        "create": [IsAuthenticated()],
        "retrieve": [IsAuthenticated()],
        "partial_update": [IsAdminOrOwner()],
        "destroy": [IsAdminOrOwner()],
    }

    def get_queryset(self) -> QuerySet[Ad]:
        """
        Получает queryset объявлений в зависимости от действия.
        """
        queryset = Ad.get_all_ads()
        if self.action == "my_ads":
            queryset = queryset.filter(author=self.request.user)
        return queryset.all()

    def get_permissions(self) -> List[BasePermission]:
        """
        Получает права доступа для текущего действия.
        """
        return self.permissions.get(self.action, [IsAuthenticated()])

    def get_serializer_class(self) -> Type[Serializer]:
        """
        Возвращает класс сериализатора для текущего действия.
        """
        if self.action in ["retrieve", "create", "partial_update", "destroy"]:
            return AdSerializer
        return AdListSerializer

    def perform_create(self, serializer: Serializer) -> None:
        """
        Сохраняет новый объект при помощи сериализатора,
        устанавливая атрибут 'author' как текущий пользователь.

        :param serializer: Сериализатор для сохранения объекта.
        """
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["GET"], url_path="me")
    def my_ads(self, request: Request, *args, **kwargs) -> Response:
        """
        Возвращает список объявлений текущего пользователя.
        :param request: HTTP-запрос.
        """
        return super().list(self, request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для работы с отзывами.
    """

    queryset = Review.get_all_reviews()
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    serializer_class = ReviewSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    permissions = {
        "list": [IsAuthenticated()],
        "create": [IsAuthenticated()],
        "retrieve": [IsAuthenticated()],
        "partial_update": [IsAdminOrOwner()],
        "destroy": [IsAdminOrOwner()],
    }

    def get_permissions(self) -> List[BasePermission]:
        """
        Получает права доступа для текущего действия.
        """
        return self.permissions.get(self.action, [IsAuthenticated()])

    def get_queryset(self) -> QuerySet[Review]:
        """
        Получает queryset отзывов для определенного объявления.
        """
        ad_id = self.kwargs.get("ad_pk")
        ad = get_object_or_404(Ad, id=ad_id)
        return ad.reviews.all()

    def perform_create(self, serializer: Serializer) -> None:
        """
         Сохраняет новый отзыв,
         связывая его с текущим пользователем и объявлением.
        :param serializer:Сериализатор для сохранения объекта.
        """
        user = self.request.user
        ad_id = self.kwargs.get("ad_pk")
        ad = get_object_or_404(Ad, id=ad_id)
        serializer.save(author=user, ad=ad)
