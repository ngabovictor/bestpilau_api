from django.urls import path, include
from rest_framework.routers import DefaultRouter

from products.views import ProductCategoryViewSet, ProductViewSet
routes = DefaultRouter(trailing_slash=False)
routes.register('categories', ProductCategoryViewSet, basename='categories')
routes.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(routes.urls))
]