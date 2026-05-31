from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import NovoUsuarioForm
from .models import Profile

# Limite de tamanho do upload (5 MB).
MAX_UPLOAD = 5 * 1024 * 1024
TIPOS_OK = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


@login_required
def perfil(request):
    p, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Trocar tema (claro/escuro)
        if 'tema' in request.POST:
            tema = request.POST.get('tema')
            if tema in dict(Profile.TEMA_CHOICES):
                p.tema = tema
                p.save()
                messages.success(request, 'Tema atualizado.')
            return redirect('perfil')

        # Remover foto
        if 'remover' in request.POST:
            if p.avatar:
                p.avatar.delete(save=False)
                p.avatar = None
                p.save()
                messages.success(request, 'Foto removida.')
            return redirect('perfil')

        # Enviar nova foto
        foto = request.FILES.get('avatar')
        if not foto:
            messages.error(request, 'Selecione uma imagem.')
        elif foto.size > MAX_UPLOAD:
            messages.error(request, 'Imagem muito grande (máx. 5 MB).')
        elif foto.content_type not in TIPOS_OK:
            messages.error(request, 'Formato inválido. Use JPG, PNG, WEBP ou GIF.')
        else:
            p.avatar = foto
            p.save()
            messages.success(request, 'Foto de perfil atualizada.')
        return redirect('perfil')

    # 'login_metodo' vem do context processor (accounts.context_processors.perfil)
    return render(request, 'accounts/profile.html', {'perfil': p})


@login_required
def registrar(request):
    """Cadastro de novos usuários — somente administradores (is_staff)."""
    if not request.user.is_staff:
        raise PermissionDenied('Apenas administradores podem cadastrar usuários.')

    if request.method == 'POST':
        form = NovoUsuarioForm(request.POST)
        if form.is_valid():
            novo = form.save()
            messages.success(request, f'Usuário "{novo.username}" criado com sucesso.')
            return redirect('registrar')
    else:
        form = NovoUsuarioForm()

    return render(request, 'accounts/registrar.html', {'form': form})
