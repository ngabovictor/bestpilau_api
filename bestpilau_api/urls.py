from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Best Pilau API",
        default_version='v1',
        description="Best Pilau universal API",
        terms_of_service="https://www.bestpilau.com",
        contact=openapi.Contact(email="info@bestpilau.com"),
        license=openapi.License(name="Private License"),
    ),
    url=os.getenv('APP_HOST'),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('authentication.urls')),
    path('', include('notifications.urls')),
    path('', include('orders.urls')),
    path('', include('payments.urls')),
    path('', include('outlets.urls')),
    path('', include('products.urls')),
    path('', include('coupons.urls')),
    path('', include('publications.urls')),
    path('', include('stats.urls')),
]

if settings.DEBUG and not eval(settings.USE_S3_BOTO3_STORAGE):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

