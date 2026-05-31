from django.contrib import admin
from .models import Registro


class Dados(admin.ModelAdmin):
    list_display = ('id', 'Sensor', 'data', 'hora', 'temperatura', 'pressao', 'altitude', 'umidade', 'data_registro')
    list_display_links = ('id', 'Sensor')
    search_fields = ('Sensor__sensor',)
    list_per_page = 50
    ordering = ('data_registro',)


admin.site.register(Registro, Dados)
