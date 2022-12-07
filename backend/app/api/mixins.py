from rest_framework import viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)


class RetrieveListModelMixin(RetrieveModelMixin, ListModelMixin, viewsets.GenericViewSet):  # todo: -> mixins.py
    pass


class ListCreateDestroyModelMixin(ListModelMixin, CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):  # todo: -> mixins.py
    pass


class CreateDestroyModelMixin(CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):  # todo: -> mixins.py
    pass