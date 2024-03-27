from django.contrib.admin import ModelAdmin, register

from recipes.models import (
    Ingredient,
    RecipeIngredient,
    Recipe,
    Tag,
    ShoppingCart,
    Favorite,
)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ("pk", "name", "author", "get_favorites", "pub_date")
    list_filter = ("author", "name", "tags")
    search_fields = ("name",)

    def get_favorites(self, obj):
        return obj.favorite_recipe.count()

    get_favorites.short_description = "Количество добавлений"


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("pk", "name", "color", "slug")


@register(RecipeIngredient)
class IngredientInRecipe(ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")
