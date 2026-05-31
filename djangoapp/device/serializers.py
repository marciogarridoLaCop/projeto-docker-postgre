from rest_framework import serializers
from .models import Tipo, Sensor


class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = ['id', 'nome']


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'sensor', 'tipo', 'local', 'macaddress',
                  'longitude', 'latitude', 'observacao', 'data_cadastro']
