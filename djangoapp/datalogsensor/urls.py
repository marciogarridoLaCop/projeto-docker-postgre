from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import RegistroViewSet, ListaRegistro

router = DefaultRouter()
router.register(r'registros', RegistroViewSet, basename='registro')

urlpatterns = router.urls + [
    path('registros/sensor/<int:pk>/', ListaRegistro.as_view(), name='lista-registro-sensor'),
]
