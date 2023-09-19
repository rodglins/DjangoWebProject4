"""
Definition of forms.
"""
from datetime import timezone, timedelta
from django import forms
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget,Select2Widget
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Cidade, RegistroLivros, Autores, Assunto, Tombo, Emprestimo



"""
Definition of forms users:
"""

class UsuarioForm2(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'rua', 'id_cidade', 'telefone']


"""
Definition of forms admin:
"""

class EmprestimoForm(forms.ModelForm):

    id_tombo_input = forms.IntegerField(label="ID do Tombo")

    class Meta:
        model = Emprestimo
        fields = ['id_usuario', 'id_tombo_input', 'id_tipos_de_emprestimos']



class TomboForm(forms.ModelForm):
    class Meta:
        model = Tombo
        fields = ['exemplar', 'id_tipo_aquisicao', 'data_aquisicao', 'id_registro_livros', 'preco']




#class LivroForm(forms.ModelForm):
#    class Meta:
#        model = RegistroLivros
#        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma', 'autores_registro_livros']

#    autores_registro_livros = forms.ModelMultipleChoiceField(
#        queryset=Autores.objects.all(),
#        label='Autores',
#        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
#        required=False
#    )

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.fields['autores_registro_livros'].widget.attrs.update({
#            'class': 'select2',
#            'data-placeholder': 'Pesquisar autores',
#            'data-minimum-input-length': 2
#        })


class LivroForm(forms.ModelForm):
    class Meta:
        model = RegistroLivros
        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma', 'autores_registro_livros', 'assuntos_registro_livros']

    autores_registro_livros = forms.ModelMultipleChoiceField(
        queryset=Autores.objects.all(),
        label='Autores',
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    assuntos_registro_livros = forms.ModelMultipleChoiceField(
        queryset=Assunto.objects.all(),
        label='Assuntos',
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assuntos_registro_livros'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Pesquisar assuntos',
            'data-minimum-input-length': 2
        })



class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'rua', 'id_cidade', 'telefone', 'email', 'id_tipos_de_usuarios']

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Personalize o widget do campo de cidade
        self.fields['id_cidade'].widget = forms.Select(choices=[(cidade.id, cidade.nome) for cidade in Cidade.objects.all()])






class ISBNForm(forms.Form):
    isbn = forms.CharField(label='ISBN', max_length=13)


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))