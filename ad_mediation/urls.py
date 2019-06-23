from django.urls import path, include
from rest_framework import routers
from .views import BackendViewSet

app_name = 'ad_mediation'

router = routers.SimpleRouter()
router.register('backends', BackendViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
