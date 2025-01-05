from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Outlet
from .serializers import OutletSerializer
from authentication.permissions import IsAdminOrReadOnly
import base64
import uuid
from rest_framework.response import Response
from rest_framework import status


class OutletViewSet(ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = [IsAdminOrReadOnly]
    
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
        serializer = self.get_serializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None, *args, **kwargs):
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
    
    def partial_update(self, request, pk=None, *args, **kwargs):
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
