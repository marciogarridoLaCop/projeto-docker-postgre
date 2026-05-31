from django.contrib.auth.models import User
from django.db import models

try:
    from PIL import Image
except ImportError:  # Pillow é instalado via requirements; evita quebrar imports em dev sem ele.
    Image = None

# Lado máximo (px) para o avatar — fotos maiores são reduzidas no upload.
AVATAR_MAX = 400


def avatar_path(instance, filename):
    """Salva como avatars/user_<id>.<ext>, sobrescrevendo a foto anterior do usuário."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    return f'avatars/user_{instance.user_id}.{ext}'


class Profile(models.Model):
    TEMA_CHOICES = [('dark', 'Escuro'), ('light', 'Claro')]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuário'
    )
    avatar = models.ImageField(
        upload_to=avatar_path, blank=True, null=True, verbose_name='Foto de perfil'
    )
    tema = models.CharField(
        max_length=5, choices=TEMA_CHOICES, default='dark', verbose_name='Tema'
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Redimensiona a imagem para no máximo AVATAR_MAX px, mantendo proporção.
        if self.avatar and Image is not None:
            try:
                img = Image.open(self.avatar.path)
                if img.height > AVATAR_MAX or img.width > AVATAR_MAX:
                    img.thumbnail((AVATAR_MAX, AVATAR_MAX))
                    img.save(self.avatar.path)
            except (FileNotFoundError, OSError, ValueError):
                pass

    @property
    def iniciais(self):
        """Iniciais para o avatar de fallback (quando não há foto)."""
        base = (self.user.get_full_name() or self.user.username).strip()
        partes = base.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return base[:2].upper() if base else '?'
