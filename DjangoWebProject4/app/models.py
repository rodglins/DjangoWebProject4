"""
Definition of models.
"""


from django.db import models
from django_select2.forms import ModelSelect2MultipleWidget
from django import forms

# Create your models here.

class Assunto(models.Model):
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao

class Classificacao(models.Model):
    chamada = models.CharField(max_length=50, unique=True)
    assunto = models.CharField(max_length=255)

    def __str__(self):
        return self.chamada

class Idioma(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class TipoUsuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo

class Pais(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=50)

class Estado(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='estados')

class Cidade(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cidades')


class Editora(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, null=True)
    ano_fundacao = models.DateField(null=True)

    def __str__(self):
        return self.nome



class Autores(models.Model):
    primeiro_nome = models.CharField(max_length=50, null=True)
    nome_do_meio = models.CharField(max_length=50, null=True)
    ultimo_nome = models.CharField(max_length=50, null=True)
    id_cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True)
    data_nascimento = models.DateField(null=True)

    def __str__(self):
        return f"{self.primeiro_nome} {self.nome_do_meio} {self.ultimo_nome}"

class RegistroLivros(models.Model):
    titulo = models.CharField(max_length=255)
    id_editora = models.ForeignKey(Editora, on_delete=models.SET_NULL, null=True)
    ano_publicacao = models.IntegerField(null=True)
    edicao = models.CharField(max_length=50, null=True)
    isbn = models.CharField(max_length=20, null=True)
    numero_paginas = models.IntegerField(null=True)
    resumo = models.TextField(null=True)
    notas = models.TextField(null=True)
    id_chamada = models.ForeignKey(Classificacao, on_delete=models.SET_NULL, null=True)
    idioma = models.ForeignKey(Idioma, on_delete=models.SET_NULL, null=True)
    autores_registro_livros = models.ManyToManyField('Autores', through='AutoresRegistroLivros', related_name='livros_autores')
    assuntos_registro_livros = models.ManyToManyField('Assunto', through='AssuntosRegistroLivros', related_name='livros_assuntos')

    def __str__(self):
        return self.titulo

class AutoresRegistroLivros(models.Model):
    autores = models.ForeignKey('Autores', on_delete=models.SET_NULL, null=True, related_name='autores_registros_livros')
    registro_livros = models.ForeignKey(RegistroLivros, on_delete=models.SET_NULL, null=True, related_name='autores_registros_livros')

    def __str__(self):
        return f'{self.autores} - {self.registro_livros}'


class AssuntosRegistroLivros(models.Model):
    assunto = models.ForeignKey('Assunto', on_delete=models.SET_NULL, null=True, related_name='assuntos_registros_livros')
    registro_livros = models.ForeignKey(RegistroLivros, on_delete=models.SET_NULL, null=True, related_name='assuntos_registros_livros')

    def __str__(self):
        return f'{self.assunto} - {self.registro_livros}'


class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14)
    rua = models.CharField(max_length=255, null=True, blank=True)
    id_cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    id_tipos_de_usuarios = models.ForeignKey(TipoUsuario, on_delete=models.SET_NULL, null=True)

class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True, default='')
    title = models.CharField(max_length=255, default='')
    url = models.URLField(default=list)
    authors = models.JSONField(default=list)
    isbn_10 = models.CharField(max_length=10, default='')
    isbn_13 = models.CharField(max_length=13, default='')
    openlibrary_key = models.CharField(max_length=255, default='')
    publishers = models.JSONField(default=list)
    publish_date = models.CharField(max_length=20, default='')
    notes = models.TextField(default=list)
    cover_small = models.URLField(default=list)
    cover_medium = models.URLField(default=list)
    cover_large = models.URLField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.isbn

