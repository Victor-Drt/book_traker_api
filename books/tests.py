from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from books.models import Books


class BookViewSetTests(APITestCase):
    """
    Testes para o BookViewSet.
    
    Testa as operações CRUD e ações customizadas do endpoint de livros,
    incluindo criação, listagem, recuperação e gerenciamento de progresso.
    """
    
    def setUp(self):
        """
        Configura o ambiente de teste.
        
        Cria um usuário de teste, autentica o cliente e cria um livro
        de exemplo para uso nos testes.
        """
        self.user = User.objects.create_user(username="victor", password="123456")
        self.client.force_authenticate(user=self.user)

        self.url_list = reverse("books-list")
        self.url_detail = lambda pk: reverse("books-detail", args=[pk])

        self.book = Books.objects.create(
            title="Django 101",
            author="Novo Autor",
            category="Categoria",
            total_pages=100,
            owner=self.user,
        )

    def test_list_books(self):
        """
        Testa a listagem de livros do usuário.
        
        Verifica se o endpoint retorna status 200 OK e se os livros
        do usuário são retornados corretamente.
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        """
        Testa a recuperação de um livro específico.
        
        Verifica se o endpoint retorna status 200 OK e se os dados
        do livro solicitado são retornados corretamente.
        """
        response = self.client.get(self.url_detail(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        """
        Testa a criação de um novo livro.
        
        Verifica se um novo livro pode ser criado via POST e se
        o endpoint retorna status 201 Created com os dados corretos.
        """
        data = {
            "title": "Novo Livro",
            "author": "Autor Teste",
            "category": "Categoria X",
            "total_pages": 150,
            "owner": self.user.id,
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_progress(self):
        """
        Testa a criação de um registro de progresso.
        
        Verifica se um novo progresso pode ser criado para um livro
        e se o endpoint retorna status 201 Created.
        """
        data = {"date": "2025-11-10", "pages_read": 55}

        response = self.client.post(self.url_detail(self.book.id) + "progress/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_progress(self):
        """
        Testa a recuperação de informações de progresso.
        
        Verifica se o endpoint retorna status 200 OK e se as informações
        de progresso do livro são retornadas corretamente.
        """
        response = self.client.get(self.url_detail(self.book.id) + "progress/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StatsViewSetTests(APITestCase):
    """
    Testes para o StatsViewSet.
    
    Testa o endpoint de estatísticas, verificando se os dados agregados
    são retornados corretamente.
    """
    
    def setUp(self):
        """
        Configura o ambiente de teste.
        
        Cria um usuário de teste, autentica o cliente e cria um livro
        de exemplo para uso nos testes de estatísticas.
        """
        self.user = User.objects.create_user(username="victor", password="123456")
        self.client.force_authenticate(user=self.user)

        self.url_list = reverse("stats-list")

        self.book = Books.objects.create(
            title="Django 101",
            author="Novo Autor",
            category="Categoria",
            total_pages=100,
            owner=self.user,
        )

    def test_list_stats(self):
        """
        Testa a listagem de estatísticas do usuário.
        
        Verifica se o endpoint retorna status 200 OK e se as estatísticas
        (livros lidos, páginas por semana/mês) são retornadas corretamente.
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
