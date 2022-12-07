from django.core.validators import MinValueValidator
from django.db import models

from users.models import User



class Tag(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=7)
    slug = models.SlugField(unique=True, max_length=200)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    count = models.IntegerField()
    unit = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe')
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, related_name='recipe_ingredients')
    tags = models.ManyToManyField(Tag, related_name='recipe_tags')
    cooking_time = models.IntegerField(validators=(MinValueValidator(1),))

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        blank=True
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        blank=True
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.CASCADE,
        blank=True
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE,
        blank=True
    )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True
    )
    shopping_list = models.IntegerField(validators=(MinValueValidator(0),))