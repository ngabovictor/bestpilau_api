from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import authentication, accounts, admin_views, preferences
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

routes = DefaultRouter(trailing_slash=False)

routes.register('auth', authentication.AuthViewSet, basename='auth')
routes.register('account', accounts.AccountViewSet, basename='account')
routes.register('admin-utils', admin_views.AdminViewSet, basename='admin-utils')
routes.register('user-preferences/saved-addresses', preferences.SavedAddressViewset, basename='saved-addresses')
routes.register('users', accounts.UsersViewSet, basename='users')

urlpatterns = [
    path('', include(routes.urls)),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
]