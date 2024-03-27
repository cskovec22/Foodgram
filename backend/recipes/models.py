from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


MIN_COOKING_TIME = 1
MIN_AMOUNT_INGREDIENT = 1


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField("Название", max_length=200)
    color = models.CharField(
        "Цвет в HEX",
        max_length=7,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        "Уникальный слаг",
        max_length=200,
        blank=True,
        null=True
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
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


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
        validators=[MinValueValidator(
            MIN_COOKING_TIME,
            message="Минимальное время приготовления - 1 мин."
        )]
    )
    pub_date = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ("name",)
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
        validators=[MinValueValidator(
            MIN_AMOUNT_INGREDIENT,
            message="Убедитесь, что это значение больше либо равно 1."
        )]
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
