from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='название тега')
    color = models.CharField(
        max_length=7,
        validators=(RegexValidator(r'#[0-9ABCDEF]{6}'),),
        unique=True,
        verbose_name='HEX код тега'
    )
    slug = models.SlugField(unique=True, max_length=200,
                            verbose_name='путь тега')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='название ингредиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='единицы измерения')

    class Meta:
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='автор рецепта')
    name = models.CharField(max_length=200, verbose_name='название рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='картинка рецепта'
    )
    text = models.TextField(verbose_name='описание рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipe_ingredients',
                                         through='foodgram.IngredientAmount',
                                         verbose_name='ингредиенты рецепта')
    tags = models.ManyToManyField(Tag, related_name='recipe_tags',
                                  verbose_name='теги рецепта')
    cooking_time = models.IntegerField(validators=(MinValueValidator(1),),
                                       verbose_name='время приготовления')

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient')
    amount = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='автор'
    )

    class Meta:
        unique_together = ('user', 'author')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
