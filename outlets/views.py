from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Outlet
from .serializers import OutletSerializer


class OutletViewSet(ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = [IsAuthenticated]
