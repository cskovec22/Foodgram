from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import CustomUser


MAX_LEN_TITLE = 200
MAX_LEN_TITLE_COLOR = 7
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_AMOUNT_INGREDIENT = 1
MAX_AMOUNT_INGREDIENT = 32000


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField("Название", unique=True, max_length=200)
    color = models.CharField(
        "Цвет",
        max_length=MAX_LEN_TITLE_COLOR,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Значение не является цветом в формате HEX!'
            )
        ],
    )
    slug = models.SlugField(
        "Уникальный слаг",
        unique=True,
        max_length=MAX_LEN_TITLE,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LEN_TITLE
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LEN_TITLE
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_unit"
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги"
    )
    image = models.ImageField(
        "Изображение",
        upload_to="recipes/images/"
    )
    name = models.CharField("Название", max_length=200)
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (в минутах)",
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    pub_date = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель, связывающая рецепты и ингредиенты."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_list",
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="in_recipe",
        verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(MIN_AMOUNT_INGREDIENT),
            MaxValueValidator(MAX_AMOUNT_INGREDIENT)
        ]
    )

    class Meta:
        ordering = ("recipe",)
        verbose_name = "рецепт-ингредиент"
        verbose_name_plural = "Рецепты-ингредиенты"

    def __str__(self):
        return f"{self.recipe} - {self.ingredient}"


class Favorite(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorite_user",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Рецепт"
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="shopping_user",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_recipe",
        verbose_name="Рецепт"
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"{self.user} {self.recipe}"
