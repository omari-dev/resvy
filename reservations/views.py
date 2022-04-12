from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import Table
from .serializers import TableSerializer
from .permissions import CanManageTables


class TableView(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, CanManageTables)
    queryset = Table.objects.all()
