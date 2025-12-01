from django.contrib.auth.models import User
from django.db.models import QuerySet
from typing import Dict, List, Optional

from .repository import BookRepository, ProgressRepository
from .models import Books, Progress


class BookService:
    """
    Service para lógica de negócio relacionada a Books.
    
    Contém a lógica de negócio para operações com livros, incluindo
    cálculo de progresso, recomendações e informações de leitura.
    """
    
    def __init__(self):
        """Inicializa o service com as dependências necessárias."""
        self.book_repo = BookRepository()
        self.progress_repo = ProgressRepository()
    
    def calculate_book_progress(self, book: Books, pages_read: int) -> Books:
        """
        Calcula e atualiza o progresso de um livro.
        
        Adiciona as páginas lidas ao total, recalcula o percentual
        de conclusão e marca como concluído se atingir 100%.
        
        Args:
            book (Books): Instância do livro a ser atualizado.
            pages_read (int): Páginas lidas a serem adicionadas.
            
        Returns:
            Books: Instância do livro atualizada.
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
    
    def get_book_progress_info(self, book: Books) -> Dict[str, float]:
        """
        Retorna informações de progresso formatadas de um livro.
        
        Args:
            book (Books): Instância do livro.
            
        Returns:
            dict: Dicionário contendo:
                - total_pages_by_day (int): Total de páginas lidas.
                - percent_finished (float): Percentual de conclusão.
        """
        return {
            "total_pages_by_day": book.total_pages_read,
            "percent_finished": book.percent_finished
        }
    
    def get_recommendations(self, user: User) -> Dict:
        """
        Obtém recomendações de livros baseadas nas categorias mais lidas.
        
        Analisa as categorias dos livros concluídos pelo usuário e
        retorna recomendações de livros da categoria mais lida (com pelo
        menos 3 livros), excluindo livros do próprio usuário.
        
        Args:
            user (User): Usuário para o qual gerar recomendações.
            
        Returns:
            dict: Dicionário contendo:
                - detail (str, optional): Mensagem de erro se não houver dados.
                - category (str, optional): Categoria recomendada.
                - recommendations (list): Lista de livros recomendados.
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
    """
    Service para lógica de negócio relacionada a estatísticas.
    
    Contém a lógica para cálculo e formatação de estatísticas de leitura
    do usuário, incluindo livros lidos, páginas por semana e por mês.
    """
    
    def __init__(self):
        """Inicializa o service com as dependências necessárias."""
        self.book_repo = BookRepository()
        self.progress_repo = ProgressRepository()
    
    def get_user_stats(self, user: User) -> Dict:
        """
        Retorna estatísticas completas do usuário.
        
        Calcula e formata estatísticas de leitura incluindo número de
        livros concluídos, páginas lidas por semana e por mês.
        
        Args:
            user (User): Usuário para o qual gerar estatísticas.
            
        Returns:
            dict: Dicionário contendo:
                - books_read (int): Número de livros concluídos.
                - pages_by_week (dict): Páginas lidas por semana (data: total).
                - pages_by_month (dict): Páginas lidas por mês (YYYY-MM: total).
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
    """
    Service para lógica de negócio relacionada a Progress.
    
    Contém a lógica para criação e gerenciamento de registros de progresso,
    incluindo atualização automática do progresso do livro relacionado.
    """
    
    def __init__(self):
        """Inicializa o service com as dependências necessárias."""
        self.progress_repo = ProgressRepository()
        self.book_service = BookService()
    
    def create_progress(self, book: Books, date, pages_read: int) -> Progress:
        """
        Cria um novo registro de progresso e atualiza o livro.
        
        Cria um registro de progresso e automaticamente atualiza o
        progresso do livro relacionado, recalculando percentuais e
        status de conclusão.
        
        Args:
            book (Books): Instância do livro relacionado.
            date: Data e hora da sessão de leitura.
            pages_read (int): Número de páginas lidas.
            
        Returns:
            Progress: Instância do progresso criado.
        """
        progress = self.progress_repo.create_progress(book, date, pages_read)
        self.book_service.calculate_book_progress(book, pages_read)
        return progress
