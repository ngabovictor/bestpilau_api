from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PubViewSet

routes = DefaultRouter(trailing_slash=False)

routes.register('publications', PubViewSet, basename='publications')

urlpatterns = [
    path('', include(routes.urls))
]