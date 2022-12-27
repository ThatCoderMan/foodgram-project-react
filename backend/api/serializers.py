from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import permissions, serializers

from foodgram.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import CustomUserSerializer

User = get_user_model()


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
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
        ingredient_objects = Ingredient.objects.filter(
            id__in=[ingredient.get('id') for ingredient in ingredients]
        )
        if len(ingredient_objects) != len(ingredients):
            raise serializers.ValidationError('invalid ingredient')
        for ing_obj, ingredient in zip(ingredient_objects, ingredients):
            amount = int(ingredient.get('amount'))
            if amount < 1:
                raise serializers.ValidationError('invalid amount')
            valid_ingredients.append(
                {'ingredient': ing_obj, 'amount': amount}
            )
        data['ingredients'] = valid_ingredients
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
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
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
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
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        is_subscribed = self.context.get('is_subscribed')
        if is_subscribed is not None:
            return is_subscribed
        return obj.is_subscribed

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes_count = self.context.get('recipes_count')
        if recipes_count is not None:
            return recipes_count
        return obj.recipes_count
