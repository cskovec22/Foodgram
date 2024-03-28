from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        "Адрес электронной почты",
        max_length=254,
        unique=True,
        validators=[EmailValidator],
    )
    username = models.CharField(
        "Уникальный юзернейм",
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[\w.@+-]+$",
            message="Username не соответствует шаблону."
        )]
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель подписок."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipe_author",
        verbose_name="Автор рецепта"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик"
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
