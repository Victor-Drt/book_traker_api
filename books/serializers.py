from rest_framework import serializers

from .models import Books
from .models import Progress


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['book', 'date', 'pages_read']
        read_only_fields = ['book']
