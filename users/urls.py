from django.urls import path

from users.views import CreateEmployeeView

urlpatterns = [
    path('users/register/', CreateEmployeeView.as_view(), name='user-register'),
]
