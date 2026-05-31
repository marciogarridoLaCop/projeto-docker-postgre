from django.db import models
from django.contrib.auth.models import User


class Tipo(models.Model):
    nome = models.CharField(max_length=30, blank=False, null=False, verbose_name='Tipo do sensor', unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Sensor'
        verbose_name_plural = 'Tipos de Sensor'

    def __str__(self):
        return self.nome


class Sensor(models.Model):
    sensor = models.CharField(max_length=30, blank=False, verbose_name='Nome do Sensor')
    tipo = models.ForeignKey(Tipo, blank=False, on_delete=models.CASCADE, verbose_name='Tipo')
    local = models.CharField(max_length=30, blank=False, null=False, verbose_name='Local de Instalação')
    macaddress = models.CharField(max_length=17, null=False, verbose_name='Endereço MAC', unique=True)
    longitude = models.CharField(max_length=11, null=True, blank=True, verbose_name='Longitude')
    latitude = models.CharField(max_length=11, null=True, blank=True, verbose_name='Latitude')
    observacao = models.TextField(max_length=200, blank=True, null=True, verbose_name='Observação')
    data_cadastro = models.DateField(verbose_name='Data de Cadastro')
    clientes = models.ManyToManyField(
        User,
        through='SensorUsuario',
        blank=True,
        verbose_name='Usuários com Acesso',
        related_name='sensores',
    )

    class Meta:
        ordering = ['data_cadastro']
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'

    def __str__(self):
        return self.sensor


class SensorUsuario(models.Model):
    NIVEL_CHOICES = [
        ('proprietario', 'Proprietário'),
        ('colaborador', 'Colaborador'),
    ]

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='acessos',
        verbose_name='Sensor',
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sensor_acessos',
        verbose_name='Usuário',
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='colaborador',
        verbose_name='Nível de Acesso',
    )
    desde = models.DateField(auto_now_add=True, verbose_name='Desde')

    class Meta:
        unique_together = [('sensor', 'usuario')]
        ordering = ['nivel', 'usuario__username']
        verbose_name = 'Acesso ao Sensor'
        verbose_name_plural = 'Acessos ao Sensor'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_nivel_display()}) → {self.sensor.sensor}'
