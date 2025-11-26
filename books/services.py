from django.contrib.auth.models import User
from django.db.models import QuerySet

from .repository import BookRepository, ProgressRepository
from .models import Books, Progress


class BookService:
    """Service para lógica de negócio relacionada a Books."""
    
    def __init__(self):
        self.book_repo = BookRepository()
        self.progress_repo = ProgressRepository()
    
    def calculate_book_progress(self, book: Books, pages_read: int):
        """
        Calcula e atualiza o progresso de um livro.
        
        Args:
            book: Instância do livro
            pages_read: Páginas lidas a serem adicionadas
        """
        book.total_pages_read += pages_read
        if book.total_pages > 0:
            book.percent_finished = (book.total_pages_read * 100) / book.total_pages
        else:
            book.percent_finished = 0.0
        
        # Marca como concluído se atingir 100%
        if book.percent_finished >= 100:
            book.is_finished = True
        
        book.save()
        return book
    
    def get_book_progress_info(self, book: Books):
        """
        Retorna informações de progresso formatadas de um livro.
        
        Returns:
            dict: Dicionário com informações de progresso
        """
        return {
            "avg_pages_by_day": book.total_pages_read,
            "percent_finished": book.percent_finished
        }
    
    def get_recommendations(self, user: User):
        """
        Obtém recomendações de livros baseadas nas categorias mais lidas.
        
        Args:
            user: Usuário para o qual gerar recomendações
            
        Returns:
            dict: Dicionário com categoria e lista de recomendações
        """
        category_counts = self.book_repo.get_category_counts(user)
        
        if not category_counts.exists():
            return {
                "detail": "Nenhuma leitura concluída ainda.",
                "category": None,
                "recommendations": []
            }
        
        # Encontra a primeira categoria com pelo menos 3 livros
        top_category = next(
            (c['category'] for c in category_counts if c['total'] >= 3),
            None
        )
        
        if not top_category:
            return {
                "detail": "Você ainda não leu 3 livros de nenhuma categoria.",
                "category": None,
                "recommendations": []
            }
        
        # Busca livros da mesma categoria de outros usuários
        recommended_books = self.book_repo.get_books_by_category(
            category=top_category,
            exclude_user=user,
            limit=10
        )
        
        return {
            "category": top_category,
            "recommendations": list(recommended_books)
        }


class StatsService:
    """Service para lógica de negócio relacionada a estatísticas."""
    
    def __init__(self):
        self.book_repo = BookRepository()
        self.progress_repo = ProgressRepository()
    
    def get_user_stats(self, user: User):
        """
        Retorna estatísticas completas do usuário.
        
        Args:
            user: Usuário para o qual gerar estatísticas
            
        Returns:
            dict: Dicionário com estatísticas formatadas
        """
        # Livros concluídos
        finished_books = self.book_repo.get_finished_books(user)
        readed_books = finished_books.count()
        
        # Páginas por semana
        weekly_data = self.progress_repo.get_weekly_pages(user)
        pages_by_week = {
            str(entry["week"].date()): entry["total_pages"]
            for entry in weekly_data
        }
        
        # Páginas por mês
        monthly_data = self.progress_repo.get_monthly_pages(user)
        pages_by_month = {
            entry["month"].strftime("%Y-%m"): entry["total_pages"]
            for entry in monthly_data
        }
        
        return {
            "books_read": readed_books,
            "pages_by_week": pages_by_week,
            "pages_by_month": pages_by_month,
        }


class ProgressService:
    """Service para lógica de negócio relacionada a Progress."""
    
    def __init__(self):
        self.progress_repo = ProgressRepository()
        self.book_service = BookService()
    
    def create_progress(self, book: Books, date, pages_read: int):
        """
        Cria um novo registro de progresso e atualiza o livro.
        
        Args:
            book: Instância do livro
            date: Data do progresso
            pages_read: Páginas lidas
            
        Returns:
            Progress: Instância criada
        """
        progress = self.progress_repo.create_progress(book, date, pages_read)
        self.book_service.calculate_book_progress(book, pages_read)
        return progress
