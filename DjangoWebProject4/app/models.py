"""
Definition of models.
"""

from django.db import models
# Create your models here.

class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True, default='')
    title = models.CharField(max_length=255, default='')
    url = models.URLField(default=list)
    authors = models.JSONField(default=list)
    isbn_10 = models.CharField(max_length=10, default='')
    isbn_13 = models.CharField(max_length=13, default='')
    openlibrary_key = models.CharField(max_length=255, default='')
    publishers = models.JSONField(default=list)
    publish_date = models.CharField(max_length=20, default='')
    notes = models.TextField(default=list)
    cover_small = models.URLField(default=list)
    cover_medium = models.URLField(default=list)
    cover_large = models.URLField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.isbn

