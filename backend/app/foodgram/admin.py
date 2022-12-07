from django.contrib import admin

from users.models import User

from .models import Favorite, Follow, Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'text', 'cooking_time', 'view_tag_list', 'view_ingredient_list')
    empty_value_display = '-пусто-'

    def view_tag_list(self, obj):
        tags = Recipe.tags.through.objects.filter(id=obj.id)
        tags_list = ''
        for tag in tags:
            tag = Tag.objects.get(pk=tag.id)
            tags_list += tag.name + ' '
        return tags_list
    view_tag_list.short_description = 'Tag'

    def view_ingredient_list(self, obj):
        ingredients = Recipe.ingredients.through.objects.filter(id=obj.id)
        ingredients_list = ''
        for ingredient in ingredients:
            ingredient = Ingredient.objects.get(pk=ingredient.id)
            ingredients_list += ingredient.name + ' '
        return ingredients_list
    view_ingredient_list.short_description = 'Ingredient'


@admin.register(Favorite)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    # def view_recipe_list(self, obj):
    #     recipes = Favorite.recipe.through.objects.filter(id=obj.id)
    #     recipes_list = ''
    #     for recipe in recipes:
    #         recipe = Recipe.objects.get(pk=recipe.id)
    #         recipes_list += recipe.title + ' '
    #     return recipes_list
    # view_recipe_list.short_description = 'Favorite'


@admin.register(Follow)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

    # def view_author_list(self, obj):
    #     authors = Follow.author.through.objects.filter(id=obj.id)
    #     authors_list = ''
    #     for author in authors:
    #         author = User.objects.get(pk=author.id)
    #         authors_list += author.username + ' '
    #     return authors_list
    # view_author_list.short_description = 'Follow'

