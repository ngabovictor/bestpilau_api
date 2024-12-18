from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer
from django.core.files.base import ContentFile
import base64
import uuid

class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.filter(state=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProductCategory.objects.filter(state=True)
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated and user.outlet_set.exists():
            # Get categories from outlets where user works
            return queryset.filter(outlet__workers=user)

        # All other users can see all categories
        return queryset


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(state=True)
    serializer_class = ProductSerializer 
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['outlet', 'category', 'is_available']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(state=True)
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated and user.outlet_set.exists():
            # Get products from outlets where user works
            return queryset.filter(outlet__workers=user)

        # All other users can see all products
        return queryset
    
    def create(self, request, *args, **kwargs):
        if 'image' in request.data and request.data['image']:
            # Get the base64 encoded image data
            image_data = request.data['image']
            # Remove data URI prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            # Decode base64 to image file
            image_file = ContentFile(content=base64.b64decode(image_data), name='{}.jpg'.format(uuid.uuid4()))
            request.data['image'] = image_file
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if 'image' in request.data and request.data['image']:
            # Get the base64 encoded image data
            image_data = request.data['image']
            # Remove data URI prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            # Decode base64 to image file
            image_file = ContentFile(content=base64.b64decode(image_data), name='{}.jpg'.format(uuid.uuid4()))
            request.data['image'] = image_file
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        if 'image' in request.data and request.data['image']:
            # Get the base64 encoded image data
            image_data = request.data['image']
            # Remove data URI prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            # Decode base64 to image file
            image_file = ContentFile(content=base64.b64decode(image_data), name='{}.jpg'.format(uuid.uuid4()))
            request.data['image'] = image_file
        return super().partial_update(request, *args, **kwargs)
    
