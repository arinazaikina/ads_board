import django_filters

from app_ads.models import Ad


class AdFilter(django_filters.rest_framework.FilterSet):
    """
    Фильтр для объявлений.
    Позволяет фильтровать объявления по заголовку (title) с учетом регистра,
    используя оператор содержания "icontains".

    Attrs:
        - title: Фильтр по заголовку объявления с оператором "icontains".

    Meta attrs:
        - model: Класс модели, к которой будет применяться фильтр.
        - fields: Поля модели, по которым разрешено применять фильтр. В данном случае, только 'title'.
    """

    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Ad
        fields = ("title",)
