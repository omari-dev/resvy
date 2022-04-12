from rest_framework import routers

from .views import TableView

router = routers.DefaultRouter()

router.register('tables', TableView, basename='tables-api')

urlpatterns = router.urls
