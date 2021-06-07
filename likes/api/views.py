from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.decorators import required_params
from likes.api.serializers import LikeSerializer, LikeSerializerForCreate, LikeSerializerForCancel
from likes.models import Like
from rest_framework.decorators import action
from inbox.services import NotificationService

class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(method='POST', params=['content_type', 'object_id'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data = request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance= serializer.create(serializer.validated_data)
        return Response(
            LikeSerializer(instance).data,
            status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def cancel(self, request):
        serializer = LikeSerializerForCancel(
            data = request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = serializer.cancel()
        return Response({
            'success': True,
            'deleted': deleted,
        }, status=status.HTTP_200_OK)

