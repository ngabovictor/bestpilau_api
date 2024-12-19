from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FdiCallbackView, TransactionViewSet

routes = DefaultRouter(trailing_slash=False)
routes.register('transactions', TransactionViewSet, basename='transactions')


urlpatterns = [
    path('', include(routes.urls)),
    path('payments/fdi/callback', FdiCallbackView.as_view(), name='fdi-callback')
]