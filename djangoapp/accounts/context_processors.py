from allauth.socialaccount.models import SocialAccount

from .models import Profile


def perfil(request):
    """Disponibiliza o perfil e o método de login do usuário em todos os templates."""
    if not request.user.is_authenticated:
        return {}
    p, _ = Profile.objects.get_or_create(user=request.user)
    # Como entrou nesta sessão (marcado no login); fallback p/ sessões antigas.
    metodo = request.session.get('logou_com')
    if metodo is None:
        tem_google = SocialAccount.objects.filter(user=request.user, provider='google').exists()
        metodo = 'google' if tem_google else 'local'
    return {'perfil': p, 'login_metodo': metodo}
