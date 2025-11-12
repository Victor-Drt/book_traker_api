from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from books.models import Books


class BookViewSetTests(APITestCase):
    def setUp(self):
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
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        response = self.client.get(self.url_detail(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        data = {
            "title": "Novo Livro",
            "author": "Autor Teste",
            "category": "Categoria X",
            "total_pages": 150,
            "owner": self.user.id
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
