from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscribeDetail,
                    SubscriptionsList, TagViewSet)

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/subscribe/', SubscribeDetail.as_view()),
    path('users/subscriptions/', SubscriptionsList.as_view())
]
