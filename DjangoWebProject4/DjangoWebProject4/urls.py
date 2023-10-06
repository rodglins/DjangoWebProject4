"""
Definition of urls for DjangoWebProject4.
"""

from datetime import datetime
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.conf import settings
from django.conf.urls.static import static
from django_select2 import urls as select2_urls



urlpatterns = [
    path('search_results/', views.search_results, name='search_results'),
    path('resultado_query/', views.resultado_query, name='resultado_query'),
    path('devolucao/', views.devolucao, name='devolucao'),
    path('editar_cadastro/', views.editar_cadastro, name='editar_cadastro'),
    path('meus_emprestimos/', views.meus_emprestimos, name='meus_emprestimos'),
    path('admin-config/', views.admin_config_page, name='admin_config_page'),
    #path('admin_custom_links/', views.admin_custom_links, name='admin_custom_links'),
    path('get-emprestimos/<int:user_id>/', views.get_emprestimos, name='get_emprestimos'),    
    path('atualizar_emprestimo/', views.atualizar_emprestimo, name='atualizar_emprestimo'),
    path('listar_emprestimos_usuario/<int:usuario_id>/', views.listar_emprestimos_usuario, name='listar_emprestimos_usuario'),
    path('registro_emprestimo/', views.registro_emprestimo, name='registro_emprestimo'),
    path('registro_livros_form/', views.registro_livros_form, name='registro_livros_form'),
    path('exibir_registro/', views.exibir_registro, name='exibir_registro'),
    path('adicionar_tombo/', views.adicionar_tombo, name='adicionar_tombo'),
    #path('teste/', views.teste_view, name='teste'),
    path('select2/', include(select2_urls)),
    path('cadastrar_livro/', views.cadastrar_livro, name='cadastrar_livro'),
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('search_books/', views.search_books, name='search_books'),
    path('search/', views.search_and_save, name='search'),
    path('grafico/', views.grafico, name='grafico'),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             },
             redirect_authenticated_user=True,  # Isso redirecionará usuários já autenticados
         ),
         name='login'),
    path('redirecionar_apos_login/', views.redirecionar_apos_login, name='redirecionar_apos_login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
