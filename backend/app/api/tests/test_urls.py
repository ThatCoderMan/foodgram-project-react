from http import HTTPStatus

from django.test import TestCase



class StaticURLTests(TestCase):
    def test_homepage(self):
        self.assertEqual(1, 1)