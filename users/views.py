from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated


from .models import User
from .permissions import CanAddEmployee
from .serializers import CreateEmployeeSerializer


class CreateEmployeeView(CreateAPIView):
    model = User
    permission_classes = (IsAuthenticated, CanAddEmployee, )
    serializer_class = CreateEmployeeSerializer
    queryset = User.objects.none()
