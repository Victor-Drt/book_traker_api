from rest_framework import serializers

from .models import Books, Progress


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Books.
    
    Serializa e deserializa dados de livros, incluindo todos os campos
    do modelo. Utilizado para operações CRUD via API REST.
    
    Fields:
        Todos os campos do modelo Books são incluídos.
    """
    class Meta:
        model = Books
        fields = '__all__'


class ProgressSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Progress.
    
    Serializa e deserializa dados de progresso de leitura.
    O campo 'book' é somente leitura e é definido automaticamente
    pelo contexto da requisição.
    
    Fields:
        book: ID do livro (read-only).
        date: Data da sessão de leitura.
        pages_read: Número de páginas lidas.
    """
    class Meta:
        model = Progress
        fields = ['book', 'date', 'pages_read']
        read_only_fields = ['book']

