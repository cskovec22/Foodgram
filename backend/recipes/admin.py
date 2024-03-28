from django.contrib.admin import ModelAdmin, TabularInline, register

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    list_editable = ("name", "measurement_unit")


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ("pk", "name", "author", "get_favorites", "pub_date")
    list_filter = ("author", "name", "tags")
    search_fields = ("name",)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    def get_favorites(self, obj):
        return obj.favorite_recipe.count()

    get_favorites.short_description = "Количество добавлений"


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    list_editable = ("name", "color", "slug")


@register(RecipeIngredient)
class IngredientInRecipe(ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")
