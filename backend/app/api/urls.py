from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, TagViewSet)

router = SimpleRouter()
shopping_cart_router = SimpleRouter()
favorite_router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('subscriptions', FollowViewSet, basename='subscriptions')
router.register('ingredients', IngredientViewSet, basename='ingredients')
shopping_cart_router.register('download_shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
favorite_router.register('favorite', FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('', include(router.urls)),
    path('recipes/', include(shopping_cart_router.urls)),
    path('recipes/<int:id>/', include(favorite_router.urls)),
    #path('', include('djoser.urls.jwt')),  todo: JWT
]
