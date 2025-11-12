from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.db.models.functions import TruncWeek, TruncMonth

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import BookSerializer, ProgressSerializer
from .models import Books, Progress


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Books.objects.filter(owner=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post', 'get'])
    def progress(self, request, pk=None):
        book = get_object_or_404(Books, pk=pk)

        if request.method == "POST":
            serializer = ProgressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(book=book)
            book.calculate_progress(serializer.data.get('pages_read'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        progress = {
            "avg_pages_by_day": book.total_pages_read, # ajustar
            "percent_finished": book.percent_finished
        }

        # progress = Progress.objects.filter(book=book.id)
        # serializer = ProgressSerializer(progress, many=True)
        return Response(progress, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        user = request.user

        category_counts = (
            Books.objects.filter(owner=user, is_finished=True)
            .values('category')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        if not category_counts.exists():
            return Response({"detail": "Nenhuma leitura concluída ainda."}, status=200)

        top_category = next(
            (c['category'] for c in category_counts if c['total'] >= 3),
            None
        )

        if not top_category:
            return Response(
                {"detail": "Você ainda não leu 3 livros de nenhuma categoria."},
                status=200
            )

        # Busca livros da mesma categoria, de outros usuários
        recommended_books = Books.objects.filter(
            category=top_category
        ).exclude(owner=user)[:10]  # limita a 10 resultados

        serializer = BookSerializer(recommended_books, many=True)
        return Response({
            "category": top_category,
            "recommendations": serializer.data
        })


class StatsViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user

        books = Books.objects.filter(owner=user, is_finished=True)
        readed_books = books.count()

        progresses = Progress.objects.filter(book__owner=user)

        weekly_data = (
            progresses.annotate(week=TruncWeek("date"))
            .values("week")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("week")
        )

        pages_by_week = {
            str(entry["week"].date()): entry["total_pages"]
            for entry in weekly_data
        }

        monthly_data = (
            progresses.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_pages=Sum("pages_read"))
            .order_by("month")
        )

        pages_by_month = {
            entry["month"].strftime("%Y-%m"): entry["total_pages"]
            for entry in monthly_data
        }

        data = {
            "books_read": readed_books,
            "pages_by_week": pages_by_week,
            "pages_by_month": pages_by_month,
        }

        return Response(data, status=status.HTTP_200_OK)
