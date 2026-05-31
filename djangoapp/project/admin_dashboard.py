from device.models import Sensor, Tipo
from datalogsensor.models import Registro


def dashboard_callback(request, context):
    if request.user.is_superuser:
        sensor_qs = Sensor.objects.all()
    else:
        sensor_qs = Sensor.objects.filter(cliente=request.user)

    sensor_count = sensor_qs.count()
    tipo_count = Tipo.objects.count()
    registro_count = Registro.objects.count()

    recent = (
        Registro.objects
        .select_related('Sensor')
        .order_by('-data_registro')[:8]
    )

    context.update({
        "kpis": [
            {
                "title": "Sensores",
                "metric": sensor_count,
                "icon": "sensors",
                "description": "Sensores cadastrados",
                "link": "/admin/device/sensor/",
                "color": "blue",
            },
            {
                "title": "Tipos de Sensor",
                "metric": tipo_count,
                "icon": "category",
                "description": "Categorias disponíveis",
                "link": "/admin/device/tipo/",
                "color": "violet",
            },
            {
                "title": "Leituras",
                "metric": f"{registro_count:,}".replace(",", "."),
                "icon": "data_table",
                "description": "Registros no banco",
                "link": "/admin/datalogsensor/registro/",
                "color": "emerald",
            },
        ],
        "recent_readings": recent,
    })
    return context
