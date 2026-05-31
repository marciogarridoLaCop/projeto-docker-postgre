from rest_framework.routers import DefaultRouter
from .views import TipoViewSet, SensorViewSet

router = DefaultRouter()
router.register(r'tipos', TipoViewSet)
router.register(r'sensores', SensorViewSet)

urlpatterns = router.urls
