from django.contrib import admin

from app_ads.models import Ad, Review


class BaseAdmin(admin.ModelAdmin):
    """
    Базовый класс администратора для моделей.
    Разрешает доступ только для суперпользователей и пользователей с ролью 'admin'.
    """

    def has_module_permission(self, request) -> bool:
        """
        Проверка прав на доступ к модулю.
        """
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """
        Проверка прав на просмотр объектов.
        """
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Проверка прав на изменение объектов.
        """
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """
        Проверка прав на удаление объектов.
        """
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False

    def has_add_permission(self, request) -> bool:
        """
        Проверка прав на добавление объектов.
        """
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False


class AdAdmin(BaseAdmin):
    """
    Конфигурация административного интерфейса для модели Ad.
    """

    list_display = ["id", "title", "price", "author", "created_at"]
    list_display_links = ["title"]


class ReviewAdmin(BaseAdmin):
    """
    Конфигурация административного интерфейса для модели Review.
    """

    list_display = ["id", "author", "ad", "created_at"]
    list_display_links = ["id"]


admin.site.register(Ad, AdAdmin)
admin.site.register(Review, ReviewAdmin)
