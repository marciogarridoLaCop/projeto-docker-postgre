from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAdapter(DefaultSocialAccountAdapter):
    """Impede que o login com Google crie contas novas.

    Apenas usuários previamente cadastrados pelo administrador podem entrar —
    o login social é casado a uma conta existente pelo e-mail
    (SOCIALACCOUNT_EMAIL_AUTHENTICATION). Quem não tiver conta é bloqueado.
    """

    def is_open_for_signup(self, request, sociallogin):
        return False
