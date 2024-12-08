from django.urls import path, include
from rest_framework.routers import DefaultRouter


routes = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(routes.urls))
]