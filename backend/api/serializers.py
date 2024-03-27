import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscriptions


class Base64ImageField(serializers.ImageField):
    """Поле для декодирования изображения."""
    def to_internal_value(self, data):
        """Преобразовать изображение."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="image." + ext)

        return super().to_internal_value(data)


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """Валидация текущего пароля."""
        user = self.context.get("request").user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Вы ввели неправильный текущий пароль!"
            )
        return value

    def validate(self, data):
        """Проверка отличия нового пароля от текущего."""
        if data.get("new_password") == data.get("current_password"):
            raise serializers.ValidationError(
                "Новый пароль равен текущему!"
            )
        return data

    def update(self, instance, validated_data):
        """Обновление пароля."""
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомного пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        ]

    def get_is_subscribed(self, obj):
        """Метод проверки подписки на автора."""
        user = self.context.get("request").user

        if user.is_authenticated:
            return Subscriptions.objects.filter(
                user=user,
                author=obj.id
            ).exists()
        return False


class CreateCustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password"
        ]

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class PostFavoriteShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]

    def get_image(self, obj):
        """Получение абсолютного URL-адреса изображения."""

        return self.context.get("request").build_absolute_uri(obj.image.url)


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для просмотра подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
        ]

    def get_recipes(self, obj):
        """Получить рецепты авторов из подписки."""
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return PostFavoriteShoppingSerializer(
            recipes, context={"request": request}, many=True
        ).data

    def get_recipes_count(self, obj):
        """Получить количество рецептов автора."""

        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "measurement_unit", "amount"]


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]

    @staticmethod
    def validate_amount(value):
        """Валидация количества ингредиента."""
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиетна должно быть больше 0."
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source="ingredients_list",
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        ]

    def get_is_favorited(self, obj):
        """Проверка, находится ли рецепт в избранном."""
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка, находится ли рецепт в избранном."""
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    ingredients = CreateIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time"
        ]

    def to_representation(self, instance):
        """Представление рецепта."""
        serializer = RecipeSerializer(
            instance,
            context={"request": self.context.get("request")}
        )
        return serializer.data

    @staticmethod
    def validate_ingredients(ingredients):
        """Валидация данных ингредиентов."""
        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент."
            )
        unique_ingredients = []
        for ingredient in ingredients:
            if ingredient["amount"] < 1:
                raise serializers.ValidationError(
                    "Убедитесь, что это значение больше либо равно 1."
                )
            if ingredient["id"] in unique_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты не должны быть одинаковыми."
                )
            unique_ingredients.append(ingredient.get("id"))

        return ingredients

    @staticmethod
    def add_ingredients_and_tags(recipe, ingredients, tags):
        """Добавить в рецепт ингредиенты и теги."""
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                amount=ingredient["amount"]
            )

    def create(self, validated_data):
        """Создать рецепт."""
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(
            author=self.context.get("request").user,
            **validated_data
        )

        self.add_ingredients_and_tags(recipe, ingredients, tags)

        return recipe

    def update(self, instance, validated_data):
        """Обновить рецепт."""
        RecipeIngredient.objects.filter(recipe=instance).delete()

        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        instance.author = self.context.get("request").user
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time",
            instance.cooking_time
        )

        self.add_ingredients_and_tags(instance, ingredients, tags)

        instance.save()

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ["id", "favorite_recipe"]
