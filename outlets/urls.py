from django.urls import path, include
from rest_framework.routers import DefaultRouter

from outlets.views import OutletViewSet


routes = DefaultRouter(trailing_slash=False)

routes.register('outlets', OutletViewSet, basename='outlet')

urlpatterns = [
    path('', include(routes.urls))
]