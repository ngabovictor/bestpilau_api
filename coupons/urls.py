from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet


routes = DefaultRouter(trailing_slash=False)
routes.register('coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(routes.urls))
]




