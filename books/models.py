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
    percent_finished = models.FloatField(default=0.0)
    total_pages_read = models.IntegerField(default=0)

    def finish_book(self):
        if self.percent_finished >= 100:
            self.is_finished = True
        self.save()

    def calculate_progress(self, pages_read):
        self.total_pages_read += pages_read
        self.percent_finished = self.total_pages_read * 100 / self.total_pages
        self.save()

class Progress(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.DateTimeField()
    pages_read = models.IntegerField(default=0)
