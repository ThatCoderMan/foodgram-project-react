from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from foodgram.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class ResponseSchemaTest(TestCase):
    tag_schema = {
        'id': int,
        'color': str,
        'slug': str
    }
    author_schema = {
        'id': int,
        'email': str,
        'username': str,
        'first_name': str,
        'last_name': str,
        'is_subscribed': bool
    }
    ingredient_schema = {
        'id': int,
        'name': str,
        'measurement_unit': str,
        'amount': int
    }
    paginated_schema = {
        'count': (int,),
        'next': (str, type(None)),
        'previous': (str, type(None))
    }
    recipe_schema = {
        'id': int,
        'tags': [tag_schema],
        'author': author_schema,
        'ingredients': [ingredient_schema],
        'is_favorited': bool,
        'is_in_shopping_cart': bool,
        'name': str,
        'image': str,
        'text': str,
        'cooking_time': int
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        cls.tag_object = Tag.objects.create(
            name='test',
            color='#FFFFFF',
            slug='test',
        )
        cls.ingredient_object = Ingredient.objects.create(
            name='test',
            measurement_unit='kg'
        )
        cls.recipe_object = Recipe.objects.create(
            author=cls.user,
            name='test',
            text='test',
            image='test.png',
            cooking_time=1
        )
        RecipeIngredient.objects.create(
            recipe=cls.recipe_object,
            ingredient=cls.ingredient_object,
            amount=1
        )
        cls.recipe_object.tags.set([cls.tag_object.id])

        cls.not_authorized_client = APIClient()
        cls.authorized_client = APIClient()
        auth_token = Token.objects.get_or_create(user=cls.user)
        auth_token = f'Token {str(auth_token[0])}'
        cls.authorized_client.credentials(HTTP_AUTHORIZATION=auth_token)

    def assertIsInstance(self, obj, cls, item_name=None):  # noqa
        if item_name is not None:
            super().assertIsInstance(
                obj,
                cls,
                f'"{item_name}" has {type(obj)} '
                f'than {cls} is expected'
            )
        else:
            super().assertIsInstance(obj, cls)

    def schema_check(self, schema, check_object):
        for item, item_type in schema.items():
            with self.subTest(f'check {item} in request obj'):
                self.assertIn(item, check_object, f'"{item}" not in request')
            if isinstance(item_type, list) and isinstance(item_type[0], dict):
                objects = check_object.get(item)
                self.assertIsInstance(objects, list, item)
                self.assertTrue(objects, f'"{item}" is empty')
                obj = objects[0]
                for include_item, include_item_type in item_type[0].items():
                    with self.subTest(f'check {include_item} in {item}'):
                        self.assertIn(
                            include_item,
                            obj,
                            f'"{include_item}" not in "{item}"'
                        )
                        self.assertIsInstance(
                            obj.get(include_item),
                            include_item_type,
                            include_item
                        )
            elif isinstance(item_type, dict):
                obj = check_object[item]
                for include_item, include_item_type in item_type.items():
                    self.assertIn(include_item, obj)
                    self.assertIsInstance(
                        obj.get(include_item),
                        include_item_type,
                        include_item
                    )
            else:
                self.assertIsInstance(check_object.get(item), item_type, item)

    def list_schema_check(self, schema, check_objects):
        self.assertIsInstance(check_objects, list, "response is not list")
        self.assertTrue(check_objects, 'response is empty list')
        check_object = check_objects[0]
        self.schema_check(schema, check_object)

    def paginated_list_schema_check(self, schema, check_objects):
        page_schema = self.paginated_schema
        for item, item_type in page_schema.items():
            self.assertIn(item, check_objects, f'"{item}" not in response')
            self.assertIsInstance(check_objects[item], item_type, item)
        self.assertIn('results', check_objects, '"results" not in response')
        self.assertIsInstance(check_objects['results'], list, 'results')
        self.assertTrue(check_objects['results'], '"results" is empty list')
        check_object = check_objects['results'][0]
        self.schema_check(schema, check_object)

    def test_user_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = f'/api/users/{str(self.user.id)}/'
        schema = self.author_schema
        request = self.authorized_client.get(test_url)
        request_objects = request.json()
        self.schema_check(schema, request_objects)

    def test_users_response_schema(self):
        test_url = '/api/users/'
        schema = self.author_schema
        request = self.authorized_client.get(test_url)
        request_objects = request.json()
        self.paginated_list_schema_check(schema, request_objects)

    def test_user_me_response_schema(self):
        test_url = '/api/users/me/'
        schema = self.author_schema
        request = self.authorized_client.get(test_url)
        request_objects = request.json()
        self.schema_check(schema, request_objects)

    def test_tags_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = '/api/tags/'
        schema = self.tag_schema
        request = self.not_authorized_client.get(test_url)
        request_objects = request.json()
        self.list_schema_check(schema, request_objects)

    def test_tag_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = f'/api/tags/{str(self.tag_object.id)}/'
        schema = self.tag_schema
        request = self.not_authorized_client.get(test_url)
        request_obj = request.json()
        self.schema_check(schema, request_obj)

    def test_ingredients_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = '/api/ingredients/'
        schema = self.ingredient_schema.copy()
        schema.pop('amount')
        request = self.not_authorized_client.get(test_url)
        request_objects = request.json()
        self.list_schema_check(schema, request_objects)

    def test_ingredient_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = f'/api/ingredients/{str(self.ingredient_object.id)}/'
        schema = self.ingredient_schema.copy()
        schema.pop('amount')
        request = self.not_authorized_client.get(test_url)
        request_obj = request.json()
        self.schema_check(schema, request_obj)

    def test_recipes_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = '/api/recipes/'
        schema = self.recipe_schema
        request = self.not_authorized_client.get(test_url)
        request_obj = request.json()
        self.paginated_list_schema_check(schema, request_obj)

    def test_recipe_response_schema(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_url = f'/api/recipes/{str(self.recipe_object.id)}/'
        schema = self.recipe_schema
        request = self.not_authorized_client.get(test_url)
        request_obj = request.json()
        self.schema_check(schema, request_obj)
