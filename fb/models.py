from django.db import models
from datetime import date


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

    fb_id = models.CharField(max_length=30, null=True, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to+')
    access_token = models.TextField(null=True, blank=True)
    hash = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    relationship_status = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES)
    significant_other = models.CharField(max_length=30, null=True, blank=True)
    progress = models.FloatField(null=True, blank=True)

    @property
    def friends(self):
        return self.relationships.all()

    @property
    def hometown(self):
        try:
            return Location.objects.get(person=self, type='H')
        except Location.DoesNotExist:
            return None

    @property
    def locations(self):
        try:
            return Location.objects.filter(person=self)
        except Location.DoesNotExist:
            return None

    @property
    def friends_travels(self):
        locations = Location.objects.filter(
            person_id__in=self.friends,
            travel_distance__isnull=False,
            type='P'
        )
        return locations

    @property
    def age(self):
        today = date.today()
        try:
            birthday = self.birthday.replace(year=today.year)
        except ValueError:
            # raised when birth date is February 29 and the current year is not a leap year
            birthday = self.birthday.replace(year=today.year, day=self.birthday.day-1)
        if birthday > today:
            return today.year - self.birthday.year - 1
        else:
            return today.year - self.birthday.year

    @property
    def friends_hometowns(self):
        locations = Location.objects.filter(
            person_id__in=self.friends,
            hometown_distance__isnull=False,
            type='H'
        )
        return locations

    def add_relationship(self, person):
        relationship, created = Relationship.objects.get_or_create(from_person=person, to_person=self)
        return relationship

    def remove_relationship(self, person):
        Relationship.objects.filter(from_person=self, to_person=person).delete()


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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    travel_distance = models.FloatField(null=True, blank=True)
    hometown_distance = models.FloatField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=LOCATION_TYPES)