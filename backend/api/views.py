import io

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from foodgram.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Subscription, Tag)

from .filters import NameSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscribeSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related('ingredients')
    serializer_class = RecipeSerializer
    filter_class = RecipeFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset.order_by('-id')
        return self.queryset.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                recipe__pk=OuterRef('pk'),
                user=user
            ))
        ).annotate(
            is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                recipe__pk=OuterRef('pk'),
                user=user
            ))
        ).order_by('-id')

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
            recipe_ingredients = RecipeIngredient.objects.filter(
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
        if not model.objects.filter(user=request.user, recipe=pk).exists():
            obj = model.objects.create(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            )
            serializer = ShortRecipeSerializer(obj.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def del_obj(self, model, request, pk):
        model.objects.filter(
            user=request.user,
            recipe=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (NameSearchFilter,)
    search_fields = ('name',)


class SubscriptionViewSet(GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(
            user=user
        ).prefetch_related('author').annotate(
            recipes_count=Count('author__recipe')
        ).annotate(
            is_subscribed=Exists(Subscription.objects.filter(
                user=user,
                author=OuterRef('author')
            ))
        ).order_by('-id')

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
        user = request.user
        subscription = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author or subscription.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscription.objects.create(
                user=user,
                author=author
            )
            recipes_count = Recipe.objects.filter(author=author).count()
            is_subscribed = Subscription.objects.filter(
                user=user,
                author=author
            ).exists()
            serializer = SubscribeSerializer(
                subscribe,
                context={
                    'request': request,
                    'is_subscribed': is_subscribed,
                    'recipes_count': recipes_count
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        subscriptions = self.get_queryset()
        paginator = CustomPagination()
        paginated_subscriptions = paginator.paginate_queryset(
            subscriptions,
            request
        )
        serializer = SubscribeSerializer(
            paginated_subscriptions,
            context={'request': request},
            many=True
        )
        return Response(
            paginator.get_paginated_response(serializer.data).data,
            status=status.HTTP_200_OK
        )
