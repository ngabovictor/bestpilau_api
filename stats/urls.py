from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stats.views import StatsViewSet


routes = DefaultRouter(trailing_slash=False)
routes.register('', StatsViewSet, basename='stats')


urlpatterns = [
    path('', include(routes.urls))
]