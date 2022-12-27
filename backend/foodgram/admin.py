from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Subscription, Tag)

User = get_user_model()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'view_favorite'
    )
    search_fields = ('name',)
    list_filter = ('tags', 'author')
    empty_value_display = '-пусто-'
    inlines = (IngredientInline,)

    def view_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    view_favorite.short_description = 'избранные'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
