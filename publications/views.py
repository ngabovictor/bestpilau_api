from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsAdminOrReadOnly
from .models import Pub
from .serializers import PubSerializer





class PubViewSet(ModelViewSet):
    queryset = Pub.objects.filter(state=True)
    serializer_class = PubSerializer
    permission_classes = [IsAdminOrReadOnly]
