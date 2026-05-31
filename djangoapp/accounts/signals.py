import requests
from allauth.account.signals import user_logged_in
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def criar_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um Profile sempre que um User é criado
    (cadastro manual, admin ou login social)."""
    if created:
        Profile.objects.create(user=instance)


def _baixar_avatar_google(profile, url):
    """Baixa a foto do Google e salva como avatar (passa pelo resize do model)."""
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and resp.content:
            profile.avatar.save('google.jpg', ContentFile(resp.content), save=True)
    except requests.RequestException:
        pass


@receiver(user_logged_in)
def registrar_metodo_login(sender, request, user, **kwargs):
    """Marca na sessão como o usuário entrou (Google x usuário/senha) e,
    em login Google sem avatar próprio, importa a foto da conta Google."""
    sociallogin = kwargs.get('sociallogin')
    request.session['logou_com'] = 'google' if sociallogin else 'local'

    if sociallogin:
        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.avatar:
            foto = (sociallogin.account.extra_data or {}).get('picture')
            if foto:
                _baixar_avatar_google(profile, foto)
