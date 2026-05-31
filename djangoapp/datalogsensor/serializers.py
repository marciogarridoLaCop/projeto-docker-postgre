from rest_framework import serializers
from django_filters import rest_framework as filters
from datetime import datetime
from .models import Registro
from device.models import Sensor


class DateFromStringFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                date_obj = datetime.strptime(value, "%d/%m/%Y").date()
            except ValueError:
                return qs.none()
            return super().filter(qs, date_obj)
        return qs


class RegistroFilter(filters.FilterSet):
    inicio = DateFromStringFilter(field_name="data_registro", lookup_expr="gte")
    fim = DateFromStringFilter(field_name="data_registro", lookup_expr="lte")

    class Meta:
        model = Registro
        fields = ['Sensor']


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class VisualizarRegistroSerializer(serializers.ModelSerializer):
    Sensor = SensorSerializer()

    class Meta:
        model = Registro
        fields = ['id', 'Sensor', 'temperatura', 'pressao', 'altitude', 'umidade', 'data_registro']


class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ['id', 'Sensor', 'temperatura', 'pressao', 'altitude', 'umidade', 'data_registro']
