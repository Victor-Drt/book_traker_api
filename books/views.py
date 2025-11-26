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


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_repo = BookRepository()
        self.book_service = BookService()
        self.progress_service = ProgressService()

    def get_queryset(self):
        return self.book_repo.get_user_books(self.request.user)

    @action(detail=True, methods=['post', 'get'])
    def progress(self, request, pk=None):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats_service = StatsService()
    
    def list(self, request):
        stats = self.stats_service.get_user_stats(request.user)
        return Response(stats, status=status.HTTP_200_OK)


class ExportHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Inicia a geração de relatório PDF em background.
        O relatório será enviado por email quando estiver pronto.
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
