import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers

from foodgram.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                             ShoppingList, Subscription, Tag)
from users.serializers import CustomUserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug', 'color')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.pk')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientAmount


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(source='ingredientamount_set',
                                              many=True,
                                              read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj.id).exists()

    def validate(self, data):
        data['author'] = self.context['request'].user

        tags = self.initial_data.get('tags')
        if not isinstance(tags, list):
            raise serializers.ValidationError('tags must be list')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError('No tag')
        data['tags'] = tags

        ingredients = self.initial_data.get('ingredients')
        if not isinstance(ingredients, list):
            raise serializers.ValidationError('ingredients must be list')
        valid_ingredients = []
        for ingredient in ingredients:
            ingredient_object = get_object_or_404(Ingredient,
                                                  id=ingredient.get('id'))
            amount = int(ingredient.get('amount'))
            if not isinstance(amount, int) or amount < 1:
                raise serializers.ValidationError('invalid amount')
            valid_ingredients.append(
                {'ingredient': ingredient_object, 'amount': amount})
        data['ingredients'] = valid_ingredients

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientAmount.objects.create(recipe=recipe,
                                            ingredient=ingredient[
                                                'ingredient'
                                            ],
                                            amount=ingredient['amount'])
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                IngredientAmount.objects.get_or_create(recipe=instance,
                                                       ingredient=ingredient[
                                                           'ingredient'
                                                       ],
                                                       amount=ingredient[
                                                           'amount'
                                                       ])

        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = obj.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        limit = self.context['limit']
        if limit:
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
