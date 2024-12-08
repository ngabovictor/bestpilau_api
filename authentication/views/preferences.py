import logging

from rest_framework.viewsets import ModelViewSet

from authentication.models import SavedAddress
from authentication.serializers.preferences import SavedAddressSerializer
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class SavedAddressViewset(ModelViewSet):
    serializer_class = SavedAddressSerializer
    permission_classes = [IsAuthenticated]
    queryset = SavedAddress.objects.filter(state=True)

    def get_queryset(self):
        return SavedAddress.objects.filter(state=True, created_by=self.request.user) if self.request.user.is_authenticated else SavedAddress.objects.none()