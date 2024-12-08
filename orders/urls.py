from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import OrderViewSet


routes = DefaultRouter(trailing_slash=False)
routes.register('orders', OrderViewSet, basename='orders')
urlpatterns = [
    path('', include(routes.urls))
]