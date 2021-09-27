from django.db import models

# Create your models here.
class Person(models.Model):
	product_name = models.CharField(max_length=30)
	product_category = models.CharField(max_length=30)

