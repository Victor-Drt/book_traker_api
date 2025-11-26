from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncWeek, TruncMonth
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import BookSerializer, ProgressSerializer
from .repository import BookRepository, ProgressRepository
from .services import BookService, StatsService, ProgressService
from .models import Books, Progress
from tasks import generate_user_report


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de livros.
    
    Fornece operações CRUD completas para livros, além de ações customizadas
    para progresso e recomendações. Todas as operações são restritas ao
    usuário autenticado e seus próprios livros.
    """
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa o ViewSet com as dependências necessárias.
        
        Configura os repositories e services utilizados pelas ações.
        """
        super().__init__(*args, **kwargs)
        self.book_repo = BookRepository()
        self.book_service = BookService()
        self.progress_service = ProgressService()

    def get_queryset(self):
        """
        Retorna o queryset de livros do usuário autenticado.
        
        Returns:
            QuerySet[Books]: QuerySet com livros do usuário ordenados
                por data de criação (mais recentes primeiro).
        """
        return self.book_repo.get_user_books(self.request.user)

    @action(detail=True, methods=['post', 'get'])
    def progress(self, request, pk=None):
        """
        Gerencia o progresso de leitura de um livro.
        
        POST: Cria um novo registro de progresso e atualiza o livro.
        GET: Retorna informações de progresso do livro.
        
        Args:
            request: Objeto de requisição HTTP.
            pk: ID do livro.
            
        Returns:
            Response: 
                - POST: Dados do progresso criado (201 Created).
                - GET: Informações de progresso (200 OK).
                - 404 Not Found: Se o livro não for encontrado.
        """
        book = self.book_repo.get_book_by_id(pk, user=request.user)
        
        if not book:
            return Response(
                {"detail": "Livro não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "POST":
            serializer = ProgressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            progress = self.progress_service.create_progress(
                book=book,
                date=serializer.validated_data['date'],
                pages_read=serializer.validated_data['pages_read']
            )
            
            return Response(
                ProgressSerializer(progress).data,
                status=status.HTTP_201_CREATED
            )

        # GET: Retorna informações de progresso
        progress_info = self.book_service.get_book_progress_info(book)
        return Response(progress_info, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        Retorna recomendações de livros baseadas nas categorias mais lidas.
        
        Analisa os livros concluídos do usuário e retorna recomendações
        de livros da categoria mais lida (com pelo menos 3 livros),
        excluindo livros do próprio usuário.
        
        Args:
            request: Objeto de requisição HTTP.
            
        Returns:
            Response: Dicionário contendo:
                - category (str): Categoria recomendada.
                - recommendations (list): Lista de livros recomendados.
                - detail (str, optional): Mensagem se não houver dados suficientes.
        """
        recommendations = self.book_service.get_recommendations(request.user)
        
        if recommendations.get("detail"):
            return Response(
                {"detail": recommendations["detail"]},
                status=status.HTTP_200_OK
            )
        
        serializer = BookSerializer(recommendations["recommendations"], many=True)
        return Response({
            "category": recommendations["category"],
            "recommendations": serializer.data
        })


class StatsViewSet(viewsets.ViewSet):
    """
    ViewSet para estatísticas de leitura do usuário.
    
    Fornece endpoints para visualização de estatísticas agregadas,
    incluindo livros lidos, páginas por semana e por mês.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa o ViewSet com as dependências necessárias.
        
        Configura o service de estatísticas utilizado.
        """
        super().__init__(*args, **kwargs)
        self.stats_service = StatsService()
    
    def list(self, request):
        """
        Retorna estatísticas completas do usuário autenticado.
        
        Calcula e retorna estatísticas agregadas incluindo número de
        livros concluídos, páginas lidas por semana e por mês.
        
        Args:
            request: Objeto de requisição HTTP.
            
        Returns:
            Response: Dicionário com estatísticas formatadas (200 OK):
                - books_read (int): Número de livros concluídos.
                - pages_by_week (dict): Páginas por semana.
                - pages_by_month (dict): Páginas por mês.
        """
        stats = self.stats_service.get_user_stats(request.user)
        return Response(stats, status=status.HTTP_200_OK)


class ExportHistoryAPIView(APIView):
    """
    API View para exportação de histórico de leitura.
    
    Permite que usuários solicitem a geração de um relatório PDF
    com seu histórico completo de leitura. A geração é processada
    em background usando Celery e o relatório é enviado por email.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Inicia a geração de relatório PDF em background.
        
        Valida se o usuário possui email cadastrado e dispara uma task
        assíncrona do Celery para gerar o relatório. O relatório será
        enviado por email quando estiver pronto.
        
        Args:
            request: Objeto de requisição HTTP.
            
        Returns:
            Response:
                - 202 Accepted: Se a geração foi iniciada com sucesso.
                - 400 Bad Request: Se o usuário não possui email cadastrado.
                - 500 Internal Server Error: Se houver erro ao iniciar a task.
        """
        user = request.user
        
        # Validar se o usuário possui email cadastrado
        if not user.email:
            return Response(
                {"error": "É necessário ter um email cadastrado para receber o relatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Disparar task assíncrona
            generate_user_report.delay(user.id)
            return Response(
                {"message": "Relatório sendo gerado. Você receberá um email em breve."},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response(
                {"error": "Erro ao iniciar geração do relatório. Tente novamente mais tarde."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
