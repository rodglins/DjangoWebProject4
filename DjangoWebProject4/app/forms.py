"""
Definition of forms.
"""

from django import forms
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget,Select2Widget
from django.contrib.auth.forms import AuthenticationForm
#from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Cidade, RegistroLivros, Autores, Assunto


#class LivroForm(forms.ModelForm):
#    autores_personalizados = forms.CharField(
#        label='Autores (separe por vírgulas)',
#        required=False,
#    )
#    autores = forms.ModelMultipleChoiceField(
#        widget=forms.CheckboxSelectMultiple,
#        required=False,  # Defina como True se quiser torná-lo obrigatório
#    )

#    class Meta:
#        model = RegistroLivros
#        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma']


#class LivroForm(forms.ModelForm):
#    autores_personalizados = forms.ModelMultipleChoiceField(
#        queryset=Autores.objects.all(),
#        label='Autores',
#        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
#        required=False
#    )

#    class Meta:
#        model = RegistroLivros
#        # Resto do código do formulário...
#        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma', 'autores_registro_livros']

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

#    def clean_autores_personalizados(self):
#        autores_personalizados = self.cleaned_data.get('autores_personalizados')

#        # Certifique-se de que autores_personalizados seja uma lista de objetos Autores válidos
#        if not isinstance(autores_personalizados, list):
#            autores_personalizados = [autores_personalizados]

#        autores_relacionados = []
#        for autor in autores_personalizados:
#            autores_relacionados.append(autor)

#        return autores_relacionados






# forms.py
from django import forms
from .models import RegistroLivros

class LivroForm(forms.ModelForm):
    class Meta:
        model = RegistroLivros
        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma', 'autores_registro_livros']

    autores_registro_livros = forms.ModelMultipleChoiceField(
        queryset=Autores.objects.all(),
        label='Autores',
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['autores_registro_livros'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Pesquisar autores',
            'data-minimum-input-length': 2
        })


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




#class LivroForm(forms.ModelForm):
#    class Meta:
#        model = RegistroLivros
#        fields = ['titulo', 'id_editora', 'ano_publicacao', 'edicao', 'isbn', 'numero_paginas', 'resumo', 'notas', 'id_chamada', 'idioma']

#    autores_personalizados = forms.ModelMultipleChoiceField(
#        queryset=Autores.objects.all(),
#        label='Autores',
#        widget=forms.SelectMultiple(attrs={'class': 'form-control select2',
#                                          'data-placeholder': 'Pesquisar autores',
#                                          'data-minimum-input-length': '2'}),
#        required=False
#    )



class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'rua', 'id_cidade', 'telefone', 'id_tipos_de_usuarios']

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