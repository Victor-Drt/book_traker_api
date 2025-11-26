from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Books(models.Model):
    """
    Modelo que representa um livro no sistema.
    
    Armazena informações sobre livros cadastrados pelos usuários,
    incluindo título, autor, categoria, progresso de leitura e
    status de conclusão.
    
    Attributes:
        title (str): Título do livro.
        author (str): Nome do autor do livro.
        category (str): Categoria/genre do livro.
        total_pages (int): Número total de páginas do livro.
        created_at (datetime): Data e hora de criação do registro.
        updated_at (datetime): Data e hora da última atualização.
        owner (User): Usuário proprietário do livro (ForeignKey).
        is_finished (bool): Indica se o livro foi concluído.
        percent_finished (float): Percentual de conclusão (0-100).
        total_pages_read (int): Total de páginas lidas até o momento.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    total_pages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    percent_finished = models.FloatField(default=0.0)
    total_pages_read = models.IntegerField(default=0)

    def finish_book(self):
        """
        Marca o livro como concluído se o percentual atingir 100%.
        
        Verifica se o percent_finished é maior ou igual a 100% e,
        caso positivo, atualiza o campo is_finished para True.
        Salva as alterações no banco de dados.
        """
        if self.percent_finished >= 100:
            self.is_finished = True
        self.save()

    def calculate_progress(self, pages_read: int):
        """
        Calcula e atualiza o progresso de leitura do livro.
        
        Adiciona as páginas lidas ao total e recalcula o percentual
        de conclusão baseado no total de páginas do livro.
        
        Args:
            pages_read (int): Número de páginas lidas a serem adicionadas.
        """
        self.total_pages_read += pages_read
        if self.total_pages > 0:
            self.percent_finished = (self.total_pages_read * 100) / self.total_pages
        else:
            self.percent_finished = 0.0
        self.save()


class Progress(models.Model):
    """
    Modelo que representa um registro de progresso de leitura.
    
    Armazena informações sobre sessões de leitura, incluindo
    a data e quantidade de páginas lidas em cada sessão.
    
    Attributes:
        book (Books): Livro relacionado ao progresso (ForeignKey).
        date (datetime): Data e hora da sessão de leitura.
        pages_read (int): Número de páginas lidas nesta sessão.
    """
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.DateTimeField()
    pages_read = models.IntegerField(default=0)
