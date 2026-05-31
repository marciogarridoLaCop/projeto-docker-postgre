from django.db import models
from device.models import Sensor


class Registro(models.Model):
    Sensor = models.ForeignKey(Sensor, blank=False, null=True, on_delete=models.CASCADE, verbose_name='Identificação do Sensor')
    data = models.CharField(max_length=10, blank=True, null=True, verbose_name='Data')
    hora = models.CharField(max_length=8, blank=True, null=True, verbose_name='Hora')
    temperatura = models.FloatField(blank=True, null=True, verbose_name='Temperatura')
    pressao = models.FloatField(blank=True, null=True, verbose_name='Pressão')
    altitude = models.FloatField(blank=True, null=True, verbose_name='Altitude')
    umidade = models.FloatField(blank=True, null=True, verbose_name='Umidade')
    data_registro = models.DateTimeField(auto_now=True, verbose_name='Data do registro')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'
