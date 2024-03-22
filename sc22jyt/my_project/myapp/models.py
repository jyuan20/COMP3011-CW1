from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)

class NewsStory(models.Model):
    category_choices = [
        ('pol', 'Politics'),
        ('art', 'Art'),
        ('tech', 'Technology'),
        ('trivia', 'Trivia'),
    ]
    region_choices = [
        ('uk', 'United Kingdom'),
        ('eu', 'Europe'),
        ('world', 'World'),
    ]

    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=6, choices=category_choices)
    region = models.CharField(max_length=5, choices=region_choices)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    details = models.CharField(max_length=128)

