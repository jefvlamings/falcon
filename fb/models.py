from django.db import models


# Create your models here.
class Person(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    RELATIONSHIP_CHOICES = (
        ('S', 'Single'),
        ('R', 'In a relationshop'),
        ('E', 'Engaged'),
        ('M', 'Married'),
        ('C', 'Its complicated'),
        ('O', 'In an open relationshop'),
        ('W', 'Widowed'),
        ('X', 'Separated'),
        ('D', 'Divorced'),
        ('U', 'In a civil union'),
        ('P', 'In a domestic partnership'),
    )
    id = models.IntegerField(primary_key=True, max_length=30)
    access_token = models.CharField(max_length=30)
    hash = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=30, null=True, blank=True)
    relationship_status = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES)
    significant_other = models.IntegerField(max_length=30, null=True, blank=True)
