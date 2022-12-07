from rest_framework import serializers

from foodgram.models import Ingredient, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug', 'color')
        model = Tag
        lookup_field = 'slug'