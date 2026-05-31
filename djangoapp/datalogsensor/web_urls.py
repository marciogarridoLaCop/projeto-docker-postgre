from django.urls import path

from . import dashboard_views

urlpatterns = [
    path('', dashboard_views.dashboard, name='dashboard'),
    path('api/sensor/<int:pk>/series/', dashboard_views.sensor_series, name='sensor-series'),
]
