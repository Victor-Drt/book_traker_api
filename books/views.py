from django.shortcuts import get_object_or_404

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
        return Books.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['post', 'get'])
    def progress(self, request, pk=None):
        book = get_object_or_404(Books, pk=pk)

        if request.method == "POST":
            serializer = ProgressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(book=book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        progress = Progress.objects.filter(book=book.id)
        serializer = ProgressSerializer(progress, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
