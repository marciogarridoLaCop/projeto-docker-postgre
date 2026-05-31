from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NovoUsuarioForm(UserCreationForm):
    """Cadastro de novo usuário — uso restrito ao administrador."""
    first_name = forms.CharField(label='Nome', max_length=150, required=True)
    email = forms.EmailField(label='E-mail', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'inp'
        self.fields['username'].widget.attrs['placeholder'] = 'ex: joao.silva'
        self.fields['username'].help_text = ''
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nome do cliente'
        self.fields['email'].widget.attrs['placeholder'] = 'cliente@email.com'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe um usuário com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        # Novos usuários são clientes comuns (sem acesso administrativo).
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
