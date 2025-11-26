from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncWeek, TruncMonth
from django.contrib.auth.models import User

from .models import Books, Progress


class BookRepository:
    """Repository para operações de acesso a dados relacionadas a Books."""
    
    @staticmethod
    def get_user_books(user: User, order_by='-created_at'):
        """Retorna todos os livros do usuário ordenados."""
        return Books.objects.filter(owner=user).order_by(order_by)
    
    @staticmethod
    def get_book_by_id(book_id: int, user: User = None):
        """Retorna um livro por ID, opcionalmente filtrado por usuário."""
        query = Books.objects.filter(pk=book_id)
        if user:
            query = query.filter(owner=user)
        return query.first()
    
    @staticmethod
    def get_finished_books(user: User):
        """Retorna todos os livros concluídos do usuário."""
        return Books.objects.filter(owner=user, is_finished=True)
    
    @staticmethod
    def get_books_by_category(category: str, exclude_user: User = None, limit: int = None):
        """Retorna livros de uma categoria, opcionalmente excluindo um usuário."""
        query = Books.objects.filter(category=category)
        if exclude_user:
            query = query.exclude(owner=exclude_user)
        if limit:
            query = query[:limit]
        return query
    
    @staticmethod
    def get_category_counts(user: User):
        """Retorna contagem de livros por categoria do usuário."""
        return (
            Books.objects.filter(owner=user, is_finished=True)
            .values('category')
            .annotate(total=Count('id'))
            .order_by('-total')
        )


class ProgressRepository:
    """Repository para operações de acesso a dados relacionadas a Progress."""
    
    @staticmethod
    def get_user_progresses(user: User):
        """Retorna todos os progressos dos livros do usuário."""
        return Progress.objects.filter(book__owner=user)
    
    @staticmethod
    def get_book_progresses(book_id: int):
        """Retorna todos os progressos de um livro."""
        return Progress.objects.filter(book_id=book_id)
    
    @staticmethod
    def create_progress(book: Books, date, pages_read: int):
        """Cria um novo registro de progresso."""
        return Progress.objects.create(
            book=book,
            date=date,
            pages_read=pages_read
        )
    
    @staticmethod
    def get_weekly_pages(user: User):
        """Retorna páginas lidas agrupadas por semana."""
        progresses = ProgressRepository.get_user_progresses(user)
        return (
            progresses.annotate(week=TruncWeek("date"))
            .values("week")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("week")
        )
    
    @staticmethod
    def get_monthly_pages(user: User):
        """Retorna páginas lidas agrupadas por mês."""
        progresses = ProgressRepository.get_user_progresses(user)
        return (
            progresses.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("month")
        )
    
    @staticmethod
    def get_total_pages_read(user: User):
        """Retorna o total de páginas lidas pelo usuário."""
        progresses = ProgressRepository.get_user_progresses(user)
        result = progresses.aggregate(total=Sum("pages_read"))
        return result["total"] or 0
