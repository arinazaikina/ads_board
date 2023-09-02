from typing import List

from django.db import models

from app_users.models import CustomUser

NULLABLE = {"blank": True, "null": True}


class Ad(models.Model):
    """
    Модель, описывающая объявление.
    """

    title = models.CharField(max_length=200, verbose_name="Название товара")
    price = models.PositiveIntegerField(verbose_name="Цена товара")
    description = models.TextField(
        verbose_name="Описание товара", max_length=1000, blank=True
    )
    author = models.ForeignKey(
        CustomUser, related_name="ads", on_delete=models.CASCADE, verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    image = models.ImageField(upload_to="ads/", verbose_name="Изображение", **NULLABLE)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        db_table = "ads"

    def __str__(self):
        return self.title

    @classmethod
    def get_all_ads(cls) -> List["Ad"]:
        """
        Возвращает список всех объявлений
        """
        return cls.objects.all().select_related("author")


class Review(models.Model):
    """
    Модель, описывающая отзыв.
    """

    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        CustomUser,
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    ad = models.ForeignKey(
        Ad, related_name="reviews", on_delete=models.CASCADE, verbose_name="Объявление"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        db_table = "reviews"

    def __str__(self):
        return f"Отзыв от {self.author} для {self.ad}"

    @classmethod
    def get_all_reviews(cls) -> List["Review"]:
        """
        Возвращает список всех отзывов
        """
        return cls.objects.all()
