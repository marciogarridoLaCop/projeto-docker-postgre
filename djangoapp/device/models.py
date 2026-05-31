from django.db import models
from django.contrib.auth.models import User


class Tipo(models.Model):
    nome = models.CharField(max_length=30, blank=False, null=False, verbose_name='Tipo do sensor', unique=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Sensor(models.Model):
    cliente = models.ForeignKey(User, null=True, blank=False, on_delete=models.CASCADE, verbose_name='Cliente')
    sensor = models.CharField(max_length=30, blank=False, verbose_name='Nome do Sensor')
    tipo = models.ForeignKey(Tipo, blank=False, on_delete=models.CASCADE)
    local = models.CharField(max_length=30, blank=False, null=False, verbose_name='Local de Instalação')
    macaddress = models.CharField(max_length=11, null=False, verbose_name='Endereço MAC', unique=True)
    longitude = models.CharField(max_length=11, null=True, verbose_name='Longitude', unique=True)
    latitude = models.CharField(max_length=11, null=True, verbose_name='Latidude', unique=True)
    observacao = models.TextField(max_length=100, blank=False, null=True, verbose_name='Observação')
    data_cadastro = models.DateField()

    class Meta:
        ordering = ['data_cadastro']

    def __str__(self):
        return self.sensor
