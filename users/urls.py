from django.urls import path

from users.views import CreateEmployeeView

urlpatterns = [
    path('users/employees/', CreateEmployeeView.as_view(), name='user-register'),
]
