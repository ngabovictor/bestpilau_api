import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from authentication.serializers.user_serializer import UserSerializer
from authentication.models import User
logger = logging.getLogger(__name__)


class AccountViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['PATCH'], detail=False, name='update-profile', url_name='update-profile',
            url_path='update-profile')
    def update_account_profile(self, request, *args, **kwargs):
        logger.info('Updating profile')
        context = {
            "request": request
        }

        serializer = UserSerializer(instance=request.user, data=request.data, partial=True, context=context)

        logger.info('Validating user input: {}'.format(request.data))
        serializer.is_valid(raise_exception=True)

        logger.info('Saving user input')
        serializer.save()
        logger.info('Saved user input: {}'.format(serializer.data))

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, name='get-profile', url_name='get-profile',
            url_path='get-profile')
    def get_account_profile(self, request, *args, **kwargs):
        logger.info('Getting profile')
        context = {
            "request": request
        }

        serializer = UserSerializer(instance=request.user, context=context)

        return Response(serializer.data, status=status.HTTP_200_OK)



class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    filterset_fields = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_rider']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name', 'created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        workers_only = self.request.query_params.get('workers_only', False)
        
        if workers_only:
            queryset = queryset.filter(is_rider=False, outlets__isnull=False).distinct()
            
        is_rider = self.request.query_params.get('is_rider', False)
        
        if not is_rider:
            queryset = queryset.exclude(is_rider=True)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

