from foodgram.models import Ingredient, Recipe, Tag

from .mixins import (CreateDestroyModelMixin, ListCreateDestroyModelMixin,
                     RetrieveListModelMixin)
from .serializers import *


class TagViewSet(RetrieveListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ListCreateDestroyModelMixin):

    queryset = Recipe.objects.all()
    serializer_class = TagSerializer


class ShoppingCartViewSet(ListCreateDestroyModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteViewSet(CreateDestroyModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FollowViewSet(ListCreateDestroyModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListModelMixin):

    queryset = Ingredient.objects.all()
    serializer_class = TagSerializer



