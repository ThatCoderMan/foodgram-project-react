from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    subscribe_detail, subscriptions_list)

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/subscribe/', subscribe_detail),
    path('users/subscriptions/', subscriptions_list)
]
