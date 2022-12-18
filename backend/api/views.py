import io

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from foodgram.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                             ShoppingList, Subscription, Tag)

from .filters import NameSearchFilter, RecipeFilter
from .mixins import RetrieveListModelMixin
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscribeSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(RetrieveListModelMixin):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    filter_class = RecipeFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission)

    @action(detail=True, methods=['post', 'delete'], name='favorite')
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(Favorite, request, pk)
        return self.del_obj(Favorite, request, pk)

    @action(detail=True, methods=['post', 'delete'], name='shopping_cart')
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(ShoppingList, request, pk)
        return self.del_obj(ShoppingList, request, pk)

    @action(detail=False, name='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        buf = io.BytesIO()
        p = canvas.Canvas(buf, pagesize=A4)
        pdfmetrics.registerFont(TTFont('font', 'fonts/arial.ttf'))
        p.setFont("font", 20)
        p.drawString(50, 780,
                     f'Список покупок пользователя {user.first_name}:')
        p.setFont("font", 14)
        shopping_list = ShoppingList.objects.filter(user=user)
        ingredients = dict()
        for ind, shopping_list_recipe in enumerate(shopping_list):
            recipe_ingredients = IngredientAmount.objects.filter(
                recipe=shopping_list_recipe.recipe
            )
            for ingredient in recipe_ingredients:
                ing_obj = ingredient.ingredient
                amount = ingredient.amount
                ingredients[ing_obj] = ingredients.get(ing_obj, 0) + amount
        for ind, (ingredient, amount) in enumerate(ingredients.items()):
            line = f'> {ingredient}({ingredient.measurement_unit}) — {amount}'
            p.drawString(65, 750 - 20 * ind, line)
        p.showPage()
        p.save()
        buf.seek(0)
        return FileResponse(
            buf,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )

    def add_obj(self, model, request, pk):
        if not model.objects.filter(user=request.user,
                                    recipe=pk).exists():
            obj = model.objects.create(user=request.user,
                                       recipe=get_object_or_404(Recipe,
                                                                id=pk))
            serializer = ShortRecipeSerializer(obj.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def del_obj(self, model, request, pk):
        obj = model.objects.filter(user=request.user,
                                   recipe=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(RetrieveListModelMixin):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (NameSearchFilter,)
    search_fields = ('name',)


@api_view(['post', 'delete'])
def subscribe_detail(request, pk):
    author = get_object_or_404(User, id=pk)
    user = request.user
    if user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    subscription = Subscription.objects.filter(user=user,
                                               author=author)
    if request.method == 'POST':
        if user == author or subscription.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscribe = Subscription.objects.create(user=user,
                                                author=author)
        serializer = SubscribeSerializer(subscribe,
                                         context={'limit': request.GET.get(
                                             'recipes_limit'
                                         )})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if subscription.exists():
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['get'])
def subscriptions_list(request):
    user = request.user
    if user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    subscriptions = Subscription.objects.filter(user=user).order_by('id')
    paginator = CustomPagination()
    paginated_subscriptions = paginator.paginate_queryset(subscriptions,
                                                          request)
    serializer = SubscribeSerializer(paginated_subscriptions,
                                     context={'limit': request.GET.get(
                                         'recipes_limit'
                                     )},
                                     many=True)
    return Response(paginator.get_paginated_response(serializer.data).data,
                    status=status.HTTP_201_CREATED)
