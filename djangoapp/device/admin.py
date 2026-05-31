import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from datalogsensor.models import Registro
from .models import Tipo, Sensor, SensorUsuario


# ── Re-register User with Unfold styling (needed for autocomplete) ────────────
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(ModelAdmin, DjangoUserAdmin):
    compressed_fields = True


# ── Inlines ───────────────────────────────────────────────────────────────────

class RegistroInline(TabularInline):
    model = Registro
    fields = ('data', 'hora', 'temperatura', 'pressao', 'umidade', 'altitude')
    readonly_fields = ('data', 'hora', 'temperatura', 'pressao', 'umidade', 'altitude')
    extra = 0
    can_delete = False
    tab = True
    verbose_name = "Leitura"
    verbose_name_plural = "Últimas 10 Leituras"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        recent_ids = list(qs.order_by('-data_registro').values_list('id', flat=True)[:10])
        return qs.filter(id__in=recent_ids).order_by('-data_registro')

    def has_add_permission(self, request, obj=None):
        return False


class SensorUsuarioInline(TabularInline):
    model = SensorUsuario
    fields = ('usuario', 'nivel', 'desde')
    readonly_fields = ('desde',)
    extra = 1
    autocomplete_fields = ('usuario',)
    tab = True
    verbose_name = "Usuário com Acesso"
    verbose_name_plural = "Usuários com Acesso"


# ── Actions ───────────────────────────────────────────────────────────────────

def exportar_tipos_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="tipos_sensor.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome', 'Total Sensores'])
    for obj in queryset:
        writer.writerow([obj.id, obj.nome, obj.sensor_set.count()])
    return response


exportar_tipos_csv.short_description = 'Exportar selecionados para CSV'


def exportar_sensores_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="sensores.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome', 'Tipo', 'Local', 'MAC', 'Latitude', 'Longitude', 'Cadastro', 'Observação', 'Usuários'])
    for obj in queryset.prefetch_related('clientes'):
        usuarios = ', '.join(u.username for u in obj.clientes.all())
        writer.writerow([
            obj.id, obj.sensor,
            obj.tipo.nome if obj.tipo else '',
            obj.local, obj.macaddress, obj.latitude, obj.longitude,
            obj.data_cadastro, obj.observacao, usuarios,
        ])
    return response


exportar_sensores_csv.short_description = 'Exportar selecionados para CSV'


# ── ModelAdmin registrations ──────────────────────────────────────────────────

@admin.register(Tipo)
class TipoAdmin(ModelAdmin):
    list_display = ('id', 'nome', 'total_sensores')
    list_display_links = ('id', 'nome')
    search_fields = ('nome',)
    list_per_page = 20
    actions = [exportar_tipos_csv]
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
    list_display = ('id', 'sensor', 'show_tipo', 'local', 'show_usuarios', 'macaddress', 'data_cadastro')
    list_display_links = ('id', 'sensor')
    search_fields = ('sensor', 'local', 'macaddress', 'clientes__username')
    list_filter = ('tipo', 'data_cadastro')
    list_per_page = 20
    list_select_related = ('tipo',)
    date_hierarchy = 'data_cadastro'
    actions = [exportar_sensores_csv]
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True
    inlines = [SensorUsuarioInline, RegistroInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('sensor', 'tipo'),
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

    @display(description='Usuários')
    def show_usuarios(self, obj):
        acessos = list(obj.acessos.select_related('usuario').order_by('nivel'))
        if not acessos:
            return format_html('<span class="text-gray-400 text-xs italic">Nenhum</span>')

        badges = []
        for a in acessos[:4]:
            cor = '#5b8def' if a.nivel == 'proprietario' else '#94a3b8'
            label = '👑' if a.nivel == 'proprietario' else ''
            badges.append(
                f'<span style="display:inline-flex;align-items:center;gap:3px;'
                f'background:{cor}1a;color:{cor};border:1px solid {cor}55;'
                f'border-radius:99px;padding:2px 8px;font-size:11px;font-weight:600;'
                f'margin:1px;">{label}{a.usuario.username}</span>'
            )
        extra = len(acessos) - 4
        html = ''.join(badges)
        if extra > 0:
            html += (
                f'<span style="color:#94a3b8;font-size:11px;margin-left:4px;">+{extra}</span>'
            )
        return format_html(html)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(clientes=request.user).distinct()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        sensor = form.instance
        if not request.user.is_superuser:
            SensorUsuario.objects.get_or_create(
                sensor=sensor,
                usuario=request.user,
                defaults={'nivel': 'proprietario'},
            )
