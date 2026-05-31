from rest_framework import viewsets, generics, filters
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Registro
from .serializers import RegistroSerializer, VisualizarRegistroSerializer, RegistroFilter


class RegistroViewSet(viewsets.ModelViewSet):
    serializer_class = RegistroSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Registro.objects.all()
        return Registro.objects.filter(Sensor__clientes=self.request.user)


class ListaRegistro(generics.ListAPIView):
    serializer_class = VisualizarRegistroSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['Sensor__sensor']
    filterset_class = RegistroFilter
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Registro.objects.filter(Sensor_id=self.kwargs['pk'])
        if self.request.user.is_superuser:
            return qs
        return qs.filter(Sensor__clientes=self.request.user)
