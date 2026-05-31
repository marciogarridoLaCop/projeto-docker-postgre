import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from datalogsensor.models import Registro
from .models import Tipo, Sensor


class RegistroInline(TabularInline):
    model = Registro
    fields = ('data', 'hora', 'temperatura', 'pressao', 'umidade', 'altitude')
    readonly_fields = ('data', 'hora', 'temperatura', 'pressao', 'umidade', 'altitude')
    extra = 0
    can_delete = False
    verbose_name = "Leitura"
    verbose_name_plural = "Últimas 10 Leituras"
    tab = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        recent_ids = list(qs.order_by('-data_registro').values_list('id', flat=True)[:10])
        return qs.filter(id__in=recent_ids).order_by('-data_registro')

    def has_add_permission(self, request, obj=None):
        return False


def exportar_sensores_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="sensores.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome', 'Tipo', 'Cliente', 'Local', 'MAC', 'Latitude', 'Longitude', 'Cadastro', 'Observação'])
    for obj in queryset:
        writer.writerow([
            obj.id, obj.sensor,
            obj.tipo.nome if obj.tipo else '',
            obj.cliente.username if obj.cliente else '',
            obj.local, obj.macaddress, obj.latitude, obj.longitude,
            obj.data_cadastro, obj.observacao,
        ])
    return response


exportar_sensores_csv.short_description = 'Exportar selecionados para CSV'


@admin.register(Tipo)
class TipoAdmin(ModelAdmin):
    list_display = ('id', 'nome', 'total_sensores')
    list_display_links = ('id', 'nome')
    search_fields = ('nome',)
    list_per_page = 20
    compressed_fields = True
    warn_unsaved_changes = True

    fieldsets = (
        ('Tipo de Sensor', {
            'fields': ('nome',),
            'description': 'Categorize os sensores por tipo para facilitar a gestão.',
        }),
    )

    @display(description='Sensores vinculados', label=True)
    def total_sensores(self, obj):
        return obj.sensor_set.count()


@admin.register(Sensor)
class SensorAdmin(ModelAdmin):
    list_display = ('id', 'sensor', 'show_tipo', 'cliente', 'local', 'macaddress', 'data_cadastro')
    list_display_links = ('id', 'sensor')
    search_fields = ('sensor', 'cliente__username', 'local', 'macaddress')
    list_filter = ('tipo', 'cliente', 'data_cadastro')
    list_per_page = 20
    list_select_related = ('cliente', 'tipo')
    date_hierarchy = 'data_cadastro'
    actions = [exportar_sensores_csv]
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True
    inlines = [RegistroInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('sensor', 'tipo', 'cliente'),
        }),
        ('Localização', {
            'fields': ('local', 'longitude', 'latitude'),
        }),
        ('Informações Técnicas', {
            'fields': ('macaddress', 'data_cadastro'),
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
    )

    @display(
        description='Tipo',
        label={
            'Temperatura': 'warning',
            'Umidade': 'info',
            'Pressão': 'primary',
            'CO2': 'danger',
            'Luminosidade': 'success',
        },
    )
    def show_tipo(self, obj):
        return obj.tipo.nome if obj.tipo else '—'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(cliente=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.cliente_id:
            obj.cliente = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if 'cliente' in form.base_fields:
                form.base_fields['cliente'].queryset = form.base_fields['cliente'].queryset.filter(
                    pk=request.user.pk
                )
        return form
