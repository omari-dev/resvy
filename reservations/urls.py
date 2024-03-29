from rest_framework import routers

from .views import TableView, ReservationView

router = routers.DefaultRouter()

router.register('tables', TableView, basename='tables-api')
router.register('reservations', ReservationView, basename='reservation-api')
urlpatterns = router.urls
