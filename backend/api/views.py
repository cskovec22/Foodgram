from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateCustomUserSerializer,
                             CreateRecipeSerializer, CreateSubscribeSerializer,
                             CustomUserSerializer, IngredientSerializer,
                             PostFavoriteShoppingSerializer, RecipeSerializer,
                             SetPasswordSerializer, SubscriptionsSerializer,
                             TagSerializer)
from api.utils import get_shopping_list
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscriptions


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет, предоставляющий действия "create", "retrieve" и "list"."""
    pass


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователя и его подписок."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Получить сериализатор."""
        if self.action == "set_password":
            return SetPasswordSerializer
        if self.action in ("subscribe", "subscriptions"):
            return SubscriptionsSerializer
        elif self.action in ("list", "retrieve", "me"):
            return CustomUserSerializer
        else:
            return CreateCustomUserSerializer

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=None
    )
    def me(self, request):
        """Просмотреть собственный профиль."""
        serializer = self.get_serializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=None
    )
    def set_password(self, request):
        """Сменить пароль."""
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            "Пароль успешно изменен.",
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписаться на автора рецепта."""
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)

        if author.recipe_author.filter(user=user).exists():
            return Response(
                f"Вы уже подписаны на автора {author.username}.",
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateSubscribeSerializer(
            author,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        Subscriptions.objects.create(user=request.user, author=author)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Отписаться от автора рецепта."""
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)

        if not author.recipe_author.filter(user=user).exists():
            return Response(
                f"Вы не подписаны на автора {author.username}.",
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscriptions.objects.get(author=author, user=user).delete()

        return Response(
            f"Вы отписались от автора {author.username}.",
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Посмотреть список подписок."""
        subscriptions = CustomUser.objects.filter(
            recipe_author__user=request.user
        )

        if subscriptions:
            paginate_subscriptions = self.paginate_queryset(subscriptions)
            serializer = self.get_serializer(
                paginate_subscriptions,
                many=True,
                context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            "У Вас нет подписок.",
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет, позволяющий получать один или несколько тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет, позволяющий получать один или несколько ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет, позволяющий получать, создавать, изменять и удалять рецепты."""
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients"
    )
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Получить сериализатор."""

        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer

        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавить рецепт в избранное."""
        user = request.user
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                "Такого рецепта не существует.",
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(pk=pk)

        if user.favorite_user.filter(recipe=recipe).exists():
            return Response(
                "Рецепт уже находится в избранном.",
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = Favorite.objects.create(user=user, recipe=recipe)
        favorite.save()

        serializer = PostFavoriteShoppingSerializer(
            recipe,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удалить рецепт из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.favorite_user.filter(recipe=recipe).exists():
            return Response(
                "Рецепт не находится в избранном.",
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.get(user=user, recipe=recipe).delete()

        return Response(
            "Рецепт удален из избранного.",
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавить ингредиенты рецепта в список покупок."""
        user = request.user
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                "Такого рецепта не существует.",
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(pk=pk)

        if user.shopping_user.filter(recipe=recipe).exists():
            return Response(
                "Рецепт уже находится в корзине.",
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart = ShoppingCart.objects.create(user=user, recipe=recipe)
        shopping_cart.save()

        serializer = PostFavoriteShoppingSerializer(
            recipe,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Убрать ингредиенты рецепта из корзины."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.shopping_user.filter(recipe=recipe).exists():
            return Response(
                "Рецепта в корзине нет.",
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.get(user=user, recipe=recipe).delete()

        return Response(
            "Ингредиенты рецепта удалены из корзины.",
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Создать файл с покупками."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(amount=Sum("amount")).order_by("ingredient__name")

        shopping_list = get_shopping_list(ingredients)
        buffer = BytesIO(shopping_list.encode("utf8"))

        return FileResponse(
            buffer,
            as_attachment=True,
            filename="shopping_list.txt"
        )
