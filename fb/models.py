from django.db import models

# Create your models here.
class Person(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Unknown'),
    )
    RELATIONSHIP_CHOICES = (
        ('S', 'Single'),
        ('R', 'In a relationshop'),
        ('E', 'Engaged'),
        ('M', 'Married'),
        ('C', 'Its complicated'),
        ('O', 'In an open relationshop'),
        ('W', 'Widowed'),
        ('Q', 'Separated'),
        ('D', 'Divorced'),
        ('U', 'In a civil union'),
        ('P', 'In a domestic partnership'),
        ('X', 'Unknown'),
    )
    fb_id = models.BigIntegerField(max_length=30, null=True, blank=True)
    access_token = models.CharField(max_length=30)
    hash = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    relationship_status = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES)
    significant_other = models.BigIntegerField(max_length=30, null=True, blank=True)