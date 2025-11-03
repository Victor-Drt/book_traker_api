from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    total_pages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)

    def finish_book(self):
        self.is_finished = not self.is_finished
        self.save()


class Progress(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.DateTimeField()
    pages_read = models.IntegerField(default=0)
