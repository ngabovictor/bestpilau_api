from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer
import base64
import uuid
from rest_framework.response import Response
from rest_framework import status


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
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request, *args, **kwargs)


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
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            # Create InMemoryUploadedFile
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import io
            image_file = InMemoryUploadedFile(
                io.BytesIO(image_bytes),
                field_name='image',
                name=f'{uuid.uuid4()}.jpg',
                content_type='image/jpeg',
                size=len(image_bytes),
                charset=None
            )
            request.data['image'] = image_file
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        if 'image' in request.data and request.data['image']:
            # Get the base64 encoded image data
            image_data = request.data['image']
            # Remove data URI prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            # Create InMemoryUploadedFile
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import io
            image_file = InMemoryUploadedFile(
                io.BytesIO(image_bytes),
                field_name='image',
                name=f'{uuid.uuid4()}.jpg',
                content_type='image/jpeg',
                size=len(image_bytes),
                charset=None
            )
            request.data['image'] = image_file
            
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        if 'image' in request.data and request.data['image']:
            # Get the base64 encoded image data
            image_data = request.data['image']
            # Remove data URI prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            # Create InMemoryUploadedFile
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import io
            image_file = InMemoryUploadedFile(
                io.BytesIO(image_bytes),
                field_name='image',
                name=f'{uuid.uuid4()}.jpg',
                content_type='image/jpeg',
                size=len(image_bytes),
                charset=None
            )
            request.data['image'] = image_file
        
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
