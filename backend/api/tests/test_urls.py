from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from foodgram.models import Tag, Recipe, Ingredient

User = get_user_model()


class URLAccessTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser',  password='testpassword')
        cls.tag_object = Tag.objects.create(
            name='test',
            color='#FFFFFF',
            slug='test',
        )
        cls.recipe_object = Recipe.objects.create(
            author=user,
            name='test',
            text='test',
            cooking_time=1
        )
        cls.ingredient_object = Ingredient.objects.create(
            name='test',
            measurement_unit='kg'
        )
        cls.not_authorized_client = APIClient()
        cls.authorized_client = APIClient()
        auth_token = Token.objects.get_or_create(user=user)
        auth_token = f'Token {str(auth_token[0])}'
        cls.authorized_client.credentials(HTTP_AUTHORIZATION=auth_token)

    def test_public_pages_exists_at_desired_location(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_urls = [
            '/api/users/',
            '/api/tags/',
            f'/api/tags/{str(self.tag_object.id)}/',
            '/api/recipes/',
            f'/api/recipes/{str(self.recipe_object.id)}/',
            '/api/ingredients/',
            f'/api/ingredients/{str(self.ingredient_object.id)}/',
        ]
        for url in test_urls:
            response = self.not_authorized_client.get(url)
            with self.subTest(response.status_code, url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_exists_at_desired_location(self):
        """
        Проверка доступности адресов доступных авторизованным пользователям
        """
        test_urls = [
            '/api/users/me/',
            '/api/recipes/download_shopping_cart/',
            '/api/users/subscriptions/'
        ]
        for url in test_urls:
            response = self.authorized_client.get(url)
            with self.subTest(response.status_code, url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
