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
        ('R', 'In a relationship'),
        ('E', 'Engaged'),
        ('M', 'Married'),
        ('C', 'Its complicated'),
        ('O', 'In an open relationship'),
        ('W', 'Widowed'),
        ('Q', 'Separated'),
        ('D', 'Divorced'),
        ('U', 'In a civil union'),
        ('P', 'In a domestic partnership'),
        ('X', 'Unknown'),
    )

    fb_id = models.BigIntegerField(max_length=30, null=True, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to+')
    access_token = models.CharField(max_length=30)
    hash = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    relationship_status = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES)
    significant_other = models.BigIntegerField(max_length=30, null=True, blank=True)

    def add_relationship(self, person):
        relationship, created = Relationship.objects.get_or_create(from_person=person, to_person=self)
        return relationship

    def remove_relationship(self, person):
        Relationship.objects.filter(from_person=self, to_person=person).delete()

    def friends(self):
        return self.relationships.all()


class Relationship(models.Model):
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')


class Location(models.Model):

    LOCATION_TYPES = (
        ('H', 'Hometown'),
        ('C', 'Current location'),
        ('P', 'Photo'),
        ('A', 'Album'),
    )

    person = models.ForeignKey('Person')
    name = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=30, null=True, blank=True)
    longitude = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=1, choices=LOCATION_TYPES)
