"""
Definition of views.
"""
import matplotlib.pyplot as plt
import requests
import certifi
import json
#from jsonfield import JSONField
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.db.models import Avg, Sum
from django.contrib import messages
from .models import Book, Cidade, TipoUsuario, RegistroLivros, Autores
from .forms import UsuarioForm, ISBNForm, LivroForm
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget,Select2Widget



#def cadastrar_livro(request):
#    if request.method == 'POST':
#        form = LivroForm(request.POST)
#        if form.is_valid():
#            form.save()
#            messages.success(request, 'Livro cadastrado com sucesso!')
#            return redirect('/cadastrar_livro')  # Redirecione para onde você deseja após o cadastro
#    else:
#        form = LivroForm()
#    return render(request, 'app/cadastro_livro.html', {'form': form})







#def cadastrar_livro(request):
#    if request.method == 'POST':
#        form = LivroForm(request.POST)
#        if form.is_valid():
#            livro = form.save(commit=False)

#            # Obtenha nomes de autores personalizados e divida em uma lista
#            autores_personalizados = request.POST.get('autores_personalizados', '')
#            autores_lista = [autor.strip() for autor in autores_personalizados.split(',')]

#            # Para cada nome de autor na lista, verifique e crie se necessário
#            autores_relacionados = []
#            for autor_nome in autores_lista:
#                # Divida o nome do autor em partes
#                partes_nome = autor_nome.split()
#                if len(partes_nome) >= 2:  # Verifique se há pelo menos um primeiro nome e um último nome
#                    primeiro_nome = partes_nome[0]
#                    ultimo_nome = partes_nome[-1]

#                    # Verifique se o autor já existe com base em primeiro_nome e ultimo_nome
#                    autor, created = Autores.objects.get_or_create(
#                        primeiro_nome=primeiro_nome,
#                        ultimo_nome=ultimo_nome
#                    )
#                    autores_relacionados.append(autor)

#            # Salve o livro
#            livro.save()

#            # Associe os autores ao livro
#            livro.autores_registro_livros.set(autores_relacionados)

#            messages.success(request, 'Livro cadastrado com sucesso!')

#            return redirect('/cadastrar_livro')  # Redirecionar para uma página de sucesso
#    else:
#        form = LivroForm()
#    return render(request, 'app/cadastro_livro.html', {'form': form})




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
    return render(request, 'app/cadastro_livro.html', {'form': form})



#def cadastrar_livro(request):
#    if request.method == 'POST':
#        form = LivroForm(request.POST)
#        if form.is_valid():
#            livro = form.save(commit=False)

#            # Obtenha nomes de autores personalizados e divida em uma lista
#            autores_personalizados = request.POST.get('autores_personalizados', '')
#            autores_lista = [autor.strip() for autor in autores_personalizados.split(',')]

#            # Para cada nome de autor na lista, verifique e crie se necessário
#            autores_relacionados = []
#            for autor_nome in autores_lista:
#                # Divida o nome do autor em partes
#                partes_nome = autor_nome.split()
#                if len(partes_nome) >= 2:  # Verifique se há pelo menos dois elementos na lista
#                    primeiro_nome = partes_nome[0]
#                    ultimo_nome = partes_nome[-1]

#                    # Verifique se o autor já existe com base em primeiro_nome e ultimo_nome
#                    autor, created = Autores.objects.get_or_create(
#                        primeiro_nome=primeiro_nome,
#                        ultimo_nome=ultimo_nome
#                    )
#                    autores_relacionados.append(autor)

#            # Salve o livro
#            livro.save()

#            # Associe os autores ao livro
#            livro.autores_registro_livros.set(autores_relacionados)

#            messages.success(request, 'Livro cadastrado com sucesso!')

#            return redirect('/cadastrar_livro')  # Redirecionar para uma pagina de sucesso
#    else:
#        form = LivroForm()
#    return render(request, 'app/cadastro_livro.html', {'form': form})




def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('/cadastrar_usuario')  # Redirecione para uma pagina de sucesso
    else:
        form = UsuarioForm()
    return render(request, 'app/cadastrar_usuario.html', {'form': form})


def search_books(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')  # Obtenha o termo de pesquisa da query string
        # Realize a pesquisa na base de dados usando o campo 'title' do modelo
        books = Book.objects.filter(title__icontains=query)
        return render(request, 'app/search_books.html', {'books': books, 'query': query})

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

                # Verificar se a editora "Penguin" está na lista de editoras
                publishers = book_data.get('publishers', [])
                if any(publisher.get('name', '').lower() == 'penguin' for publisher in publishers):
                    publishers = [{"name": "Penguin"}]

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

                return render(request, 'app/result.html', {'book': book})
    else:
        form = ISBNForm()
    
    return render(request, 'app/search.html', {'form': form})


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

    return render(request, 'app/grafico.html', context)


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
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
            'title':'Contact',
            'message':'Your contact page.',
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
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


def teste_view(request):
    return render(request, 'app/teste.html')
