from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncWeek, TruncMonth
from django.contrib.auth.models import User
from typing import Optional

from .models import Books, Progress


class BookRepository:
    """
    Repository para operações de acesso a dados relacionadas a Books.
    
    Abstrai todas as consultas ao banco de dados relacionadas ao modelo
    Books, seguindo o padrão Repository para separação de responsabilidades.
    """
    
    @staticmethod
    def get_user_books(user: User, order_by: str = '-created_at'):
        """
        Retorna todos os livros do usuário ordenados.
        
        Args:
            user (User): Usuário proprietário dos livros.
            order_by (str): Campo para ordenação. Padrão: '-created_at'.
            
        Returns:
            QuerySet[Books]: QuerySet com os livros do usuário ordenados.
        """
        return Books.objects.filter(owner=user).order_by(order_by)
    
    @staticmethod
    def get_book_by_id(book_id: int, user: Optional[User] = None):
        """
        Retorna um livro por ID, opcionalmente filtrado por usuário.
        
        Args:
            book_id (int): ID do livro a ser buscado.
            user (User, optional): Usuário para filtrar o livro. Se fornecido,
                retorna apenas se o livro pertencer ao usuário.
                
        Returns:
            Optional[Books]: Instância do livro ou None se não encontrado.
        """
        query = Books.objects.filter(pk=book_id)
        if user:
            query = query.filter(owner=user)
        return query.first()
    
    @staticmethod
    def get_finished_books(user: User):
        """
        Retorna todos os livros concluídos do usuário.
        
        Args:
            user (User): Usuário proprietário dos livros.
            
        Returns:
            QuerySet[Books]: QuerySet com livros concluídos (is_finished=True).
        """
        return Books.objects.filter(owner=user, is_finished=True)
    
    @staticmethod
    def get_books_by_category(
        category: str, 
        exclude_user: Optional[User] = None, 
        limit: Optional[int] = None
    ):
        """
        Retorna livros de uma categoria, opcionalmente excluindo um usuário.
        
        Args:
            category (str): Categoria dos livros a serem buscados.
            exclude_user (User, optional): Usuário a ser excluído dos resultados.
            limit (int, optional): Limite máximo de resultados a retornar.
            
        Returns:
            QuerySet[Books]: QuerySet com livros da categoria especificada.
        """
        query = Books.objects.filter(category=category)
        if exclude_user:
            query = query.exclude(owner=exclude_user)
        if limit:
            query = query[:limit]
        return query
    
    @staticmethod
    def get_category_counts(user: User):
        """
        Retorna contagem de livros por categoria do usuário.
        
        Agrupa os livros concluídos do usuário por categoria e retorna
        a contagem de cada categoria, ordenada por total decrescente.
        
        Args:
            user (User): Usuário proprietário dos livros.
            
        Returns:
            QuerySet: QuerySet com categorias e suas contagens, ordenado
                por total decrescente.
        """
        return (
            Books.objects.filter(owner=user, is_finished=True)
            .values('category')
            .annotate(total=Count('id'))
            .order_by('-total')
        )


class ProgressRepository:
    """
    Repository para operações de acesso a dados relacionadas a Progress.
    
    Abstrai todas as consultas ao banco de dados relacionadas ao modelo
    Progress, incluindo agregações e estatísticas de leitura.
    """
    
    @staticmethod
    def get_user_progresses(user: User):
        """
        Retorna todos os progressos dos livros do usuário.
        
        Args:
            user (User): Usuário proprietário dos livros.
            
        Returns:
            QuerySet[Progress]: QuerySet com todos os progressos dos
                livros do usuário.
        """
        return Progress.objects.filter(book__owner=user)
    
    @staticmethod
    def get_book_progresses(book_id: int):
        """
        Retorna todos os progressos de um livro específico.
        
        Args:
            book_id (int): ID do livro.
            
        Returns:
            QuerySet[Progress]: QuerySet com todos os progressos do livro.
        """
        return Progress.objects.filter(book_id=book_id)
    
    @staticmethod
    def create_progress(book: Books, date, pages_read: int):
        """
        Cria um novo registro de progresso.
        
        Args:
            book (Books): Instância do livro relacionado.
            date: Data e hora da sessão de leitura.
            pages_read (int): Número de páginas lidas.
            
        Returns:
            Progress: Instância do progresso criado.
        """
        return Progress.objects.create(
            book=book,
            date=date,
            pages_read=pages_read
        )
    
    @staticmethod
    def get_weekly_pages(user: User):
        """
        Retorna páginas lidas agrupadas por semana.
        
        Agrupa os progressos do usuário por semana e soma as páginas
        lidas em cada semana.
        
        Args:
            user (User): Usuário proprietário dos progressos.
            
        Returns:
            QuerySet: QuerySet com semanas e totais de páginas lidas,
                ordenado por semana.
        """
        progresses = ProgressRepository.get_user_progresses(user)
        return (
            progresses.annotate(week=TruncWeek("date"))
            .values("week")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("week")
        )
    
    @staticmethod
    def get_monthly_pages(user: User):
        """
        Retorna páginas lidas agrupadas por mês.
        
        Agrupa os progressos do usuário por mês e soma as páginas
        lidas em cada mês.
        
        Args:
            user (User): Usuário proprietário dos progressos.
            
        Returns:
            QuerySet: QuerySet com meses e totais de páginas lidas,
                ordenado por mês.
        """
        progresses = ProgressRepository.get_user_progresses(user)
        return (
            progresses.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("month")
        )
    
    @staticmethod
    def get_total_pages_read(user: User):
        """
        Retorna o total de páginas lidas pelo usuário.
        
        Calcula a soma de todas as páginas lidas em todos os
        progressos do usuário.
        
        Args:
            user (User): Usuário proprietário dos progressos.
            
        Returns:
            int: Total de páginas lidas. Retorna 0 se não houver progressos.
        """
        progresses = ProgressRepository.get_user_progresses(user)
        result = progresses.aggregate(total=Sum("pages_read"))
        return result["total"] or 0
