from django.contrib import admin
from .models import Tipo, Sensor


class Tipos(admin.ModelAdmin):
    list_display = ('id', 'nome')
    list_display_links = ('id', 'nome')
    search_fields = ('nome',)
    list_per_page = 20


class Sensores(admin.ModelAdmin):
    list_display = ('id', 'sensor', 'cliente', 'local', 'observacao')
    list_display_links = ('id', 'sensor')
    search_fields = ('sensor', 'cliente__username')
    list_filter = ('cliente',)
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(cliente=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.cliente_id:
            obj.cliente = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Tipo, Tipos)
admin.site.register(Sensor, Sensores)
