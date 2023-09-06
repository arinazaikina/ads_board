from typing import Any, Dict

from rest_framework import serializers

from .models import Ad, Review
from .validators import NotEmptyStringValidator


class AdSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ad, которая представляет объявление.
    """

    title = serializers.CharField(validators=[NotEmptyStringValidator()])
    description = serializers.CharField(validators=[NotEmptyStringValidator()])

    class Meta:
        model = Ad
        fields = ["pk", "image", "title", "price", "description"]
        read_only_fields = ["pk"]

    def to_representation(self, instance: Ad) -> Dict[str, Any]:
        """
        Переопределяет представление объекта.
        :param instance: Экземпляр модели Ad.
        :return: Представление объекта в виде словаря.
        """
        ad_output = super().to_representation(instance)
        ad_output["author_first_name"] = (
            instance.author.first_name if instance.author else None
        )
        ad_output["author_last_name"] = (
            instance.author.last_name if instance.author else None
        )
        ad_output["author_id"] = instance.author.id if instance.author else None
        return ad_output


class AdListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления списка объявлений (Ads).
    """

    class Meta:
        model = Ad
        fields = ["pk", "image", "title", "price", "description"]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review, представляющей отзывы.
    """

    text = serializers.CharField(validators=[NotEmptyStringValidator()])
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_first_name = serializers.CharField(
        source="author.first_name", read_only=True
    )
    author_last_name = serializers.CharField(source="author.last_name", read_only=True)
    ad_id = serializers.IntegerField(source="ad.id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    author_image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "pk",
            "text",
            "author_id",
            "ad_id",
            "created_at",
            "author_first_name",
            "author_last_name",
            "author_image",
        ]

    def get_author_image(self, obj):
        request = self.context.get("request")
        if obj.author.image:
            return request.build_absolute_uri(obj.author.image.url)
