from django.urls import include, path
from rest_framework import routers

from api.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

app_name = "api"

router = routers.DefaultRouter()

router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)
router.register("users", CustomUserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
