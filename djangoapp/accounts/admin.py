from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ('show_avatar', 'user', 'show_email', 'show_tema')
    list_display_links = ('user',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('tema',)
    list_per_page = 20
    list_select_related = ('user',)
    compressed_fields = True
    warn_unsaved_changes = True

    readonly_fields = ('show_avatar_large',)

    fieldsets = (
        ('Usuário', {
            'fields': ('user',),
        }),
        ('Personalização', {
            'fields': ('show_avatar_large', 'avatar', 'tema'),
        }),
    )

    @display(description='Avatar')
    def show_avatar(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="36" height="36"'
                ' style="border-radius:50%;object-fit:cover;border:2px solid #e2e8f0;" />',
                obj.avatar.url,
            )
        initials = obj.iniciais
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:36px;height:36px;border-radius:50%;background:#3b82f6;'
            'color:#fff;font-weight:600;font-size:13px;">{}</span>',
            initials,
        )

    @display(description='E-mail')
    def show_email(self, obj):
        return obj.user.email or '—'

    @display(description='Tema', label={'dark': 'primary', 'light': 'warning'})
    def show_tema(self, obj):
        return obj.tema or 'light'

    @display(description='Pré-visualização do avatar')
    def show_avatar_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100"'
                ' style="border-radius:50%;object-fit:cover;border:3px solid #e2e8f0;" />',
                obj.avatar.url,
            )
        initials = obj.iniciais
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:100px;height:100px;border-radius:50%;background:#3b82f6;'
            'color:#fff;font-weight:700;font-size:28px;">{}</span>',
            initials,
        )
