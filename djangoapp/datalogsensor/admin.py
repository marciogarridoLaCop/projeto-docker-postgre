import csv

from django.contrib import admin
from django.http import HttpResponse
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter, RangeNumericFilter
from unfold.decorators import display

from .models import Registro


def exportar_leituras_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="leituras_sensores.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Sensor', 'Data', 'Hora',
        'Temperatura (°C)', 'Pressão (hPa)', 'Altitude (m)', 'Umidade (%)',
        'Registrado em',
    ])
    for obj in queryset.select_related('Sensor'):
        writer.writerow([
            obj.id,
            obj.Sensor.sensor if obj.Sensor else '',
            obj.data, obj.hora,
            obj.temperatura, obj.pressao, obj.altitude, obj.umidade,
            obj.data_registro,
        ])
    return response


exportar_leituras_csv.short_description = 'Exportar selecionados para CSV'


@admin.register(Registro)
class RegistroAdmin(ModelAdmin):
    list_display = (
        'id', 'Sensor', 'data', 'hora',
        'show_temperatura', 'show_pressao', 'show_umidade', 'show_altitude',
        'data_registro',
    )
    list_display_links = ('id', 'Sensor')
    search_fields = ('Sensor__sensor',)
    list_filter = (
        'Sensor',
        ('data_registro', RangeDateTimeFilter),
        ('temperatura', RangeNumericFilter),
        ('umidade', RangeNumericFilter),
        ('pressao', RangeNumericFilter),
    )
    list_per_page = 50
    ordering = ('-data_registro',)
    list_select_related = ('Sensor',)
    date_hierarchy = 'data_registro'
    actions = [exportar_leituras_csv]
    compressed_fields = True
    list_filter_submit = True

    readonly_fields = ('data_registro',)

    fieldsets = (
        ('Sensor', {
            'fields': ('Sensor',),
        }),
        ('Data e Hora da Medição', {
            'fields': ('data', 'hora', 'data_registro'),
        }),
        ('Leituras', {
            'fields': ('temperatura', 'pressao', 'altitude', 'umidade'),
        }),
    )

    @display(description='Temperatura')
    def show_temperatura(self, obj):
        if obj.temperatura is None:
            return '—'
        return format_html(
            '<span style="font-variant-numeric: tabular-nums;">{:.1f} °C</span>',
            obj.temperatura,
        )

    @display(description='Pressão')
    def show_pressao(self, obj):
        if obj.pressao is None:
            return '—'
        return format_html(
            '<span style="font-variant-numeric: tabular-nums;">{:.1f} hPa</span>',
            obj.pressao,
        )

    @display(description='Umidade')
    def show_umidade(self, obj):
        if obj.umidade is None:
            return '—'
        return format_html(
            '<span style="font-variant-numeric: tabular-nums;">{:.1f} %</span>',
            obj.umidade,
        )

    @display(description='Altitude')
    def show_altitude(self, obj):
        if obj.altitude is None:
            return '—'
        return format_html(
            '<span style="font-variant-numeric: tabular-nums;">{:.1f} m</span>',
            obj.altitude,
        )
