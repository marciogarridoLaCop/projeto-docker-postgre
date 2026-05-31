from device.models import Sensor, Tipo
from datalogsensor.models import Registro


def dashboard_callback(request, context):
    sensor_count = Sensor.objects.count()
    tipo_count = Tipo.objects.count()
    registro_count = Registro.objects.count()

    if request.user.is_superuser:
        meus_sensores = sensor_count
    else:
        meus_sensores = Sensor.objects.filter(cliente=request.user).count()

    context.update({
        "kpis": [
            {
                "title": "Sensores Cadastrados",
                "metric": meus_sensores if not request.user.is_superuser else sensor_count,
                "icon": "sensors",
                "description": "Total de sensores no sistema" if request.user.is_superuser else "Seus sensores ativos",
            },
            {
                "title": "Tipos de Sensor",
                "metric": tipo_count,
                "icon": "category",
                "description": "Categorias disponíveis",
            },
            {
                "title": "Total de Leituras",
                "metric": f"{registro_count:,}".replace(",", "."),
                "icon": "data_table",
                "description": "Registros armazenados",
            },
        ],
    })
    return context
