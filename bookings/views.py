from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet
from .serializers import BookingSerializer
from users.permissions import IsPatient
from .models import Booking

class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    filterset_fields = ['campaign', 'status']
    search_fields = ['campaign__name']

    http_method_names = ['get', 'patch', 'put']

    def get_serializer_class(self):
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('patient', 'campaign')

        if user.role == 'PATIENT':
            return queryset.filter(patient=user)
        return queryset

    def get_permissions(self):
        if self.action in ['partial_update', 'cancel']:
            permission_classes = [IsAuthenticated, IsPatient]
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsAuthenticated, IsPatient]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.status == 'PENDING':
            serializer.save()
        else:
            raise ValidationError(
                {'detail': 'Only pending bookings can be modified'},
                code=status.HTTP_400_BAD_REQUEST
            )


    @action(detail=True, methods=['get'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        if booking.status != 'PENDING':
            return Response(
                {'detail': 'Only pending bookings can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.patient != request.user:
            return Response(
                {'detail': 'You can only cancel your own bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'CANCELLED'
        booking.save()
        return Response({'status': 'Booking cancelled successfully'})
