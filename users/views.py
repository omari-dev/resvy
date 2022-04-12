from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User
from users.permissions import CanAddEmployee
from users.serializers import CreateEmployeeSerializer


class CreateEmployeeView(CreateAPIView):
    model = User
    permission_classes = (IsAuthenticated, CanAddEmployee, )
    serializer_class = CreateEmployeeSerializer
    queryset = User.objects.none()

    def perform_create(self, serializer) -> User:
        return serializer.save()

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED, )
