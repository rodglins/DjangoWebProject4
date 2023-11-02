"""
Definition of views.
"""
import matplotlib.pyplot as plt
import requests
import certifi
import json
import mysql.connector
#from jsonfield import JSONField
from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.db import connection
from django.db.models import Avg, Sum, Q, Max, F, Value, CharField, Case, When, Subquery
from django.db.models.functions import Concat
from django.contrib import messages
from .models import Book, Cidade, TipoUsuario, RegistroLivros, AutoresRegistroLivros, Autores, Tombo, Usuario, Emprestimo, TipoDeEmprestimo, StatusEmprestimo, LimiteDeLivros, Editora
from .forms import UsuarioForm, ISBNForm, LivroForm, TomboForm, EmprestimoForm, UsuarioForm2, EditoraForm, AutoresForm
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget,Select2Widget
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import Group
from django.views.generic import View, ListView, CreateView, UpdateView
from django.urls import reverse_lazy




"""
Definition of groups:
"""

def is_users(user):
    return user.groups.filter(name='Usuarios').exists()

def is_admin(user):
    return user.groups.filter(name='Administradores').exists()

"""
Definition of index redirect:
"""

@login_required
def redirecionar_apos_login(request):
    if request.user.groups.filter(name='Usuarios').exists():
        return redirect('../meus_emprestimos')  # Redireciona para a página de empréstimos
    elif request.user.groups.filter(name='Administradores').exists():
        return redirect('../admin-config')  # Redireciona para a página de configuração de administradores
    else:
        # Caso o usuário não pertença a nenhum grupo específico, redirecione para uma página padrão
        return redirect('index')

@login_required
@user_passes_test(is_admin)
def admin_config_page(request):
    # Sua lógica para a página de administradores aqui
    return render(request, 'app/adm/admin_config_page.html')



"""
Definition users views:
"""




@login_required
@user_passes_test(is_users)
def meus_emprestimos(request):
    # Suponho que você tenha o usuário logado disponível em request.user
    # Substitua 'email_do_usuario_logado' pelo email do usuário logado
    email_do_usuario_logado = request.user.email

    # Execute a query para obter os empréstimos do usuário logado
    emprestimos = Emprestimo.objects.filter(id_usuario__email=email_do_usuario_logado)

    return render(request, 'app/users/meus_emprestimos.html', {'emprestimos': emprestimos})



@login_required
@user_passes_test(is_users)
def editar_cadastro(request):
    user_id = request.user.id  # ID do usuário logado
    usuario = get_object_or_404(Usuario, id=user_id)  # Busca o usuário com base no ID do usuário logado
    
    if request.method == 'POST':
        form = UsuarioForm2(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            # Redirecione para a página de detalhes do usuário após a atualização
            return redirect('detalhes_usuario', email=usuario.email)
    else:
        form = UsuarioForm2(instance=usuario)
    
    return render(request, 'app/users/editar_cadastro.html', {'form': form})


@user_passes_test(is_users)
def user_contact(request):
    """Renders the contact page for regular users."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/users/contact.html',
        {
            'title':'Contato',
            'message':'Entre em contato pelos meios abaixo.',
            'year':datetime.now().year,
        }
    )

@user_passes_test(is_users)
def user_about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/users/about.html',
        {
            'title':'Sobre nos',
            'message':'Este e o catalogo de livros da biblioteca.',
            'year':datetime.now().year,
        }
    )


"""
Definition admin views:
"""



@user_passes_test(is_admin)
def get_emprestimos(request, user_id):
    emprestimos = Emprestimo.objects.filter(id_usuario=user_id, status_emprestimo_id=1).values('id')

    return JsonResponse({'emprestimos': list(emprestimos)})

@user_passes_test(is_admin)
def atualizar_emprestimo(request):
    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario')
        id_emprestimo = request.POST.get('id_emprestimo')

        # Verifique se o usuário e o empréstimo existem e têm o status correto (1)
        try:
            usuario = Usuario.objects.get(id=id_usuario)
            emprestimo = Emprestimo.objects.get(id=id_emprestimo, id_usuario=usuario, status_emprestimo_id=1)
        except (Usuario.DoesNotExist, Emprestimo.DoesNotExist):
            return render(request, 'app/adm/atualizar_emprestimo.html', {'usuarios': Usuario.objects.all()})

        # Atualize o status do empréstimo para 4 e a data de devolução para 7 dias adiante
        emprestimo.status_emprestimo_id = 4
        emprestimo.data_devolucao += timedelta(days=7)
        emprestimo.save()

        return redirect('listar_emprestimos_usuario', usuario_id=id_usuario)
    else:
        return render(request, 'app/adm/atualizar_emprestimo.html', {'usuarios': Usuario.objects.all()})



@user_passes_test(is_admin)
def listar_emprestimos_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    emprestimos = Emprestimo.objects.filter(id_usuario=usuario_id)
    return render(request, 'app/adm/listar_emprestimos_usuario.html', {'usuario': usuario, 'emprestimos': emprestimos})


@user_passes_test(is_admin)
def registro_emprestimo(request):
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            # Captura o valor do campo id_tombo_input e atribui ao campo id_tombo
            emprestimo = form.save(commit=False)
            emprestimo.id_tombo_id = form.cleaned_data['id_tombo_input']

            # Verifique se o Tombo com o ID fornecido existe
            try:
                tombo = Tombo.objects.get(id=emprestimo.id_tombo_id)
            except Tombo.DoesNotExist:
                form.add_error('id_tombo_input', 'O Tombo com este ID não existe.')
                return render(request, 'app/adm/registro_emprestimo.html', {'form': form})
            
             # Consulte a tabela app_limitedelivros para obter o limite do usuário com base em seu tipo de usuário
            limite_emprestimos = LimiteDeLivros.objects.filter(
                tipo_de_usuario=emprestimo.id_usuario.id_tipos_de_usuarios
            ).values('quantidade').first()

            if limite_emprestimos:
                # Verifique a quantidade atual de empréstimos em andamento para o usuário
                emprestimos_em_andamento = Emprestimo.objects.filter(
                    id_usuario=emprestimo.id_usuario,
                    status_emprestimo_id=1  # Verifique se o status é 'emprestado'
                ).count()

                if emprestimos_em_andamento >= limite_emprestimos['quantidade']:
                    form.add_error(None, "Limite de empréstimos atingido para este usuário.")
                    return render(request, 'app/adm/registro_emprestimo.html', {'form': form})


            # Verifique se já existe um empréstimo com o mesmo livro e usuário
            emprestimo_existente = Emprestimo.objects.filter(
                id_tombo=emprestimo.id_tombo_id,
                status_emprestimo_id=1  # Verifique se o status é 'emprestado'
            ).exists()

            if not emprestimo_existente:
                emprestimo.status_emprestimo = StatusEmprestimo.objects.get(id=1)  # Defina o status adequado
                emprestimo.data_emprestimo = timezone.now().date()
                tipo_emprestimo = TipoDeEmprestimo.objects.get(id=emprestimo.id_tipos_de_emprestimos.id)
                emprestimo.data_devolucao = timezone.now().date() + timedelta(days=tipo_emprestimo.prazo_em_dias)
                emprestimo.save()
                return redirect('listar_emprestimos_usuario', usuario_id=emprestimo.id_usuario.id)
            else:
                # Empréstimo duplicado, você pode tratar isso de acordo com suas necessidades
                # Neste exemplo, apenas redirecionamos de volta ao formulário com uma mensagem de erro
                form.add_error(None, "Este livro já foi emprestado.")
    else:
        form = EmprestimoForm()

    usuarios = Usuario.objects.all()  # Ou outra consulta para obter a lista de usuários
    tipo_emprestimo = TipoDeEmprestimo.objects.all()

    return render(request, 'app/adm/registro_emprestimo.html', {'form': form, 'usuarios': usuarios, 'tipo_emprestimo': tipo_emprestimo})



@user_passes_test(is_admin)
def devolucao(request):
    if request.method == "POST":
        id_tombo = request.POST.get("id_tombo")
        emprestimos = Emprestimo.objects.filter(id_tombo=id_tombo, status_emprestimo__in=[1, 4])

        # Atualiza o status_emprestimo para 2
        status_devolucao = StatusEmprestimo.objects.get(tipo="devolvido")
        emprestimos.update(status_emprestimo=status_devolucao)

        messages.success(request, 'Livro devolvido com sucesso!')

    return render(request, "app/adm/devolucao.html")

@user_passes_test(is_admin)
def registro_livros_form(request):
    registros = RegistroLivros.objects.all()
    selected_registro = None
    tombos = None
    form = TomboForm()

    if request.method == 'POST':
        registro_id = request.POST.get('registro_id')
        if registro_id:
            selected_registro = RegistroLivros.objects.get(pk=registro_id)
            tombos = selected_registro.tombo_set.all()

    return render(request, 'app/adm/registro_livros_form.html', {
        'registros': registros,
        'selected_registro': selected_registro,
        'tombos': tombos,
        'form': form
    })





@user_passes_test(is_admin)
def exibir_registro(request):
    if request.method == 'POST':
        registro_id = request.POST.get('registro_id')
        registro = get_object_or_404(RegistroLivros, pk=registro_id)
        tombos = Tombo.objects.filter(id_registro_livros=registro_id)
        form = TomboForm()
        return render(request, 'app/adm/cadastro_tombo.html', {'registro': registro, 'tombos': tombos, 'form': form})
    else:
        # Redirecione de volta para a página de seleção de registro
        return redirect('registro_livros_form')


@user_passes_test(is_admin)
def adicionar_tombo(request):
    if request.method == 'POST':
        # Obtenha o id_registro_livros_id do formulário
        id_registro_livros_id = request.POST.get('id_registro_livros_id')
        
        # Crie um formulário com os dados do POST
        form = TomboForm(request.POST)
        
        if form.is_valid():
            # Crie uma instância de Tombo e defina o id_registro_livros_id
            tombo = form.save(commit=False)
            tombo.id_registro_livros_id = id_registro_livros_id
            tombo.save()
            
            # Redirecionar para a página de exibição de registros
            return redirect('exibir_registro')
    else:
        form = TomboForm()
    
    return render(request, 'app/adm/cadastro_tombo.html', {'form': form})



@user_passes_test(is_admin)
def cadastrar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.save()

            # Limpe a associação anterior de assuntos
            livro.assuntos_registro_livros.clear()

            # Associe os assuntos selecionados no formulário
            assuntos_selecionados = form.cleaned_data['assuntos_registro_livros']
            livro.assuntos_registro_livros.add(*assuntos_selecionados)


            # Limpe a associação anterior de autores
            livro.autores_registro_livros.clear()

            # Associe os autores selecionados no formulário
            autores_selecionados = form.cleaned_data['autores_registro_livros']
            livro.autores_registro_livros.add(*autores_selecionados)

            messages.success(request, 'Livro cadastrado com sucesso!')
            return redirect('/cadastrar_livro')  # Redirecionar para uma pagina de sucesso

    else:
        form = LivroForm()
    return render(request, 'app/adm/cadastro_livro.html', {'form': form})



@user_passes_test(is_admin)
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('/cadastrar_usuario')  # Redirecione para uma pagina de sucesso
    else:
        form = UsuarioForm()
    return render(request, 'app/adm/cadastrar_usuario.html', {'form': form})




@user_passes_test(is_admin)
def search_and_save(request):
    if request.method == 'POST':
        form = ISBNForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['isbn']
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                json_data = response.json()

                book_data = json_data.get(f"ISBN:{isbn}", {})  # Extrair os dados específicos do livro
                authors = book_data.get('authors', [])

                # Extrair apenas o conteúdo do campo "name" de cada autor
                author_names = ', '.join([author.get('name', '') for author in authors])


                publishers = book_data.get('publishers', [])
                #if any(publisher.get('name', '').lower() == 'penguin' for publisher in publishers):
                #    publishers = [{"name": "Penguin"}]

                book, created = Book.objects.get_or_create(
                    isbn=isbn,
                    title=book_data.get('title', ''),
                    url=book_data.get('url', ''),
                    authors=author_names,
                    isbn_10=book_data.get('identifiers', {}).get('isbn_10', [''])[0],
                    isbn_13=book_data.get('identifiers', {}).get('isbn_13', [''])[0],
                    openlibrary_key=book_data.get('identifiers', {}).get('openlibrary', [''])[0],
                    publishers=publishers,  # Definir a lista de editoras corretamente
                    publish_date=book_data.get('publish_date', ''),
                    notes=book_data.get('notes', ''),
                    cover_small=book_data.get('cover', {}).get('small', ''),
                    cover_medium=book_data.get('cover', {}).get('medium', ''),
                    cover_large=book_data.get('cover', {}).get('large', '')
                )

                try:
                    connection = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='pi2023g13',
                        database='library'
                        )
                    if created:
                        # Executar a procedure para inserir na tabela app_editora
                        cursor = connection.cursor()
                        cursor.callproc('InsertIntoEditora')
                        cursor.close()
  
                        # Executar a procedure para inserir na tabela app_registrolivros
                        cursor = connection.cursor()
                        cursor.callproc('InsertIntoRegistroLivros')
                        cursor.close()
  
                        # Executar a procedure para inserir na tabela app_autores
                        cursor = connection.cursor()
                        cursor.callproc('InsertIntoAutores')
                        cursor.close()
  
                        # Executar a procedure para inserir na tabela app_autoresregistrolivros
                        cursor = connection.cursor()
                        cursor.callproc('InsertIntoAutoresRegistroLivros')
                        cursor.close()
  
                        # Confirmar a transação no banco de dados
                        connection.commit()
                    # Fechar a conexão
                    connection.close()
                except Exception as e:
                    # Lidar com erros de conexão ou execução das procedures
                    print(f"Erro ao executar as procedures: {str(e)}")


                return render(request, 'app/adm/result.html', {'book': book})
    else:
        form = ISBNForm()
    
    return render(request, 'app/adm/search.html', {'form': form})

@user_passes_test(is_admin)
def grafico(request):
    produtos = Produto.objects.all()

    # Extrair dados para o gráfico
    nomes = [produto.nome for produto in produtos]
    precos = [produto.preco for produto in produtos]

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.barh(nomes, precos)
    plt.xlabel('Preco')
    plt.ylabel('Produto')
    plt.title('Grafico de Precos dos Produtos')
    plt.tight_layout()

    # Salvar o gráfico como imagem temporária
    img_path = 'media/grafico_temp.png'
    plt.savefig(img_path)
    plt.close()

    context = {
        'img_path': img_path
    }

    return render(request, 'app/adm/grafico.html', context)


@user_passes_test(is_admin)
def resultado_query(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                b.id as tombo,
                STRING_AGG(CONCAT(aa2.ultimo_nome, ', ', aa2.primeiro_nome), ' ; ') AS autores,
                a.titulo, a.ano_publicacao, a.edicao, c.nome, d.chamada, b.exemplar,
                CASE
                    WHEN f.tipo = 'devolvido' THEN 'disponível'
                    WHEN f.tipo = 'renovado' THEN 'emprestado'
                    WHEN f.tipo = 'emprestado' THEN 'emprestado'
                    WHEN f.tipo = 'atrasado' THEN 'emprestado'
                    ELSE 'disponível'
                END AS tipo
            FROM app_registrolivros a
            INNER JOIN app_autoresregistrolivros aa ON aa.registro_livros_id = a.id
            INNER JOIN app_autores aa2 ON aa2.id = aa.autores_id
            INNER JOIN app_tombo b ON a.id = b.id_registro_livros_id
            INNER JOIN app_editora c ON a.id_editora_id = c.id
            INNER JOIN app_classificacao d ON a.id_chamada_id = d.id
            LEFT JOIN app_emprestimo e ON e.id_tombo_id = b.id
            LEFT JOIN app_statusemprestimo f ON f.id = e.status_emprestimo_id
            WHERE e.id = (
                SELECT MAX(id)
                FROM app_emprestimo
                WHERE id_tombo_id = e.id_tombo_id 
            )
            GROUP BY b.id, a.titulo, a.ano_publicacao, a.edicao, c.nome, d.chamada, b.exemplar, f.tipo, e.data_devolucao
            ORDER BY a.titulo
        """)
        results = cursor.fetchall()

    context = {'results': results}
    return render(request, 'app/adm/resultado_query.html', context)



@user_passes_test(is_admin)
def editora_list(request):
    editoras = Editora.objects.all()
    return render(request, 'app/adm/editora/editora_list.html', {'editoras': editoras})






@user_passes_test(is_admin)
def editora_create(request):
    if request.method == 'POST':
        form = EditoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('editora-list')
    else:
        form = EditoraForm()
    return render(request, 'app/adm/editora/editora_form.html', {'form': form})

@user_passes_test(is_admin)
def editora_edit(request, editora_id):
    editora = Editora.objects.get(pk=editora_id)
    if request.method == 'POST':
        form = EditoraForm(request.POST, instance=editora)
        if form.is_valid():
            form.save()
            return redirect('editora-list')
    else:
        form = EditoraForm(instance=editora)
    return render(request, 'app/adm/editora/editora_form.html', {'form': form})








def criar_autor(request):
    if request.method == 'POST':
        form = AutoresForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar ou fazer qualquer outra ação após o salvamento do autor.
    else:
        form = AutoresForm()

    return render(request, 'app/adm/criar_autor.html', {'form': form})










"""
Definition open views:
"""




def search_results(request):
    search_query = request.GET.get('q', '')

    autores_subquery = AutoresRegistroLivros.objects.filter(
        Q(autores__ultimo_nome__icontains=search_query) |
        Q(autores__primeiro_nome__icontains=search_query)
    ).values('registro_livros__id')

    results = (
    RegistroLivros.objects
    .filter(
        Q(titulo__icontains=search_query) |
        Q(id__in=Subquery(autores_subquery))
    )
    .annotate(
        autores=Concat(
            F('autores_registro_livros__autores__primeiro_nome'),
            Value(' '),
            F('autores_registro_livros__autores__ultimo_nome'),
            output_field=CharField()
        ),
        assunto=Concat(
            F('id_chamada__assunto__descricao'),
            output_field=CharField()
        )
    )
    .values(
        'tombo__id',
        'autores',
        'titulo',
        'ano_publicacao',
        'edicao',
        'id_editora__nome',
        'id_chamada__chamada',
        'tombo__exemplar',
        'assunto'
    )

    .annotate(
        tipo=Case(
            When(tombo__emprestimo__status_emprestimo__tipo='devolvido', then=Value('disponível')),
            When(tombo__emprestimo__status_emprestimo__tipo='renovado', then=Value('emprestado')),
            When(tombo__emprestimo__status_emprestimo__tipo='emprestado', then=Value('emprestado')),
            When(tombo__emprestimo__status_emprestimo__tipo='atrasado', then=Value('emprestado')),
            default=Value('disponível'),
            output_field=CharField()
        )
    )
    .order_by('titulo')
)

    if search_query:
        results = results.filter(
            Q(assunto__icontains=search_query)
        )
        
    if is_admin(request.user):
        return render(request, 'app/adm/search_results.html', {'results': results})
    elif is_users(request.user):
        return render(request, 'app/users/search_results.html', {'results': results})
    else:
        return render(request, 'app/search_results.html', {'results': results})






# def search_books(request):
#     if request.method == 'GET':
#         query = request.GET.get('query', '0000')  # Obtenha o termo de pesquisa da query string
#         # Realize a pesquisa na base de dados usando o campo 'title' do modelo
#         books = Book.objects.filter(title__icontains=query)
#         return render(request, 'app/search_books.html', {'books': books, 'query': query})


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Library Tools',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contato',
            'message':'Entre em contato abaixo.',
            'year':datetime.now().year,
        }
    )


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Sobre nos',
            'message':'Este e o catalogo de livros da biblioteca.',
            'year':datetime.now().year,
        }
    )


#def teste_view(request):
#    return render(request, 'app/teste.html')

#@user_passes_test(is_admin)
#def admin_custom_links(request):
#    return render(request, 'app/admin_custom_links.html')
