from django.db import models
from books.models import Books


# Create your models here.
class Progress(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.DateTimeField()
    pages_read = models.IntegerField(default=0)
