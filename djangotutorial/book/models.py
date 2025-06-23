from django.db import models

# Create your models here.
class Book_1(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=20)
    pub_time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default=0)