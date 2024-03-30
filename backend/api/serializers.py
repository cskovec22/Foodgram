import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from users.models import CustomUser


MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_AMOUNT_INGREDIENT = 1
MAX_AMOUNT_INGREDIENT = 32000


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
        user = self.context["request"].user
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
        user = self.context["request"].user

        if user.is_authenticated:
            return user.subscriber.filter(author=obj.id).exists()

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

        return self.context["request"].build_absolute_uri(obj.image.url)


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
    amount = serializers.IntegerField(
        max_value=MAX_AMOUNT_INGREDIENT,
        min_value=MIN_AMOUNT_INGREDIENT
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
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
        user = request.user

        if request is None or user.is_anonymous:
            return False
        return user.subscriber.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка, находится ли рецепт в избранном."""
        request = self.context.get("request")
        user = request.user

        if request is None or user.is_anonymous:
            return False
        return user.subscriber.filter(recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    ingredients = CreateIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING_TIME,
        min_value=MIN_COOKING_TIME
    )

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

    def validate(self, data):
        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент."
            )

        unique_ingredients = set()

        for ingredient in ingredients:
            if not Ingredient.objects.filter(pk=ingredient.get("id")).exists():
                raise serializers.ValidationError(
                    "Такого ингредиента нет."
                )

            if ingredient.get("id") in unique_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты не должны быть одинаковыми."
                )
            unique_ingredients.add(ingredient.get("id"))

        tags = data.get("tags")

        if not tags:
            raise serializers.ValidationError(
                "Должен быть хотя бы один тег."
            )

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                "Теги не должны быть одинаковыми."
            )

        return data

    @staticmethod
    def add_ingredients_and_tags(recipe, ingredients, tags):
        """Добавить в рецепт ингредиенты и теги."""
        recipe.tags.set(tags)

        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                amount=ingredient["amount"]
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)

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


class CreateSubscribeSerializer(SubscriptionsSerializer):
    """Сериализатор для подписки и отписки от автора."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, obj):
        """Валидация подписки."""
        if self.context['request'].user == obj:
            raise serializers.ValidationError(
                "Нельзя подписаться на себя."
            )

        return obj
