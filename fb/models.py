from django.db import models
import geo


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
    progress = models.FloatField(null=True, blank=True)

    @property
    def friends(self):
        return self.relationships.all()

    @property
    def furthest_travelers(self):
        friends = self.friends
        travelers_by_distance = []
        for friend in friends:
            if friend.furthest_travel is None:
                continue
            else:
                travelers_by_distance += friend.furthest_travel
        return sorted(travelers_by_distance, key=lambda k: k['distance'])

    @property
    def furthest_travel(self):
        if not self.travels[::-1][:1]:
            return None
        else:
            return self.travels[::-1][:1]

    @property
    def travels(self):
        travels_by_distance = []
        for location in self.locations:
            distance = self.distance_between_locations(self.hometown, location)
            if distance is None:
                continue
            else:
                travels_by_distance.append({
                    'distance': distance,
                    'location': location,
                    'person': self
                })
        return sorted(travels_by_distance, key=lambda k: k['distance'])

    @property
    def friends_hometowns(self):
        friends = self.friends
        hometowns_by_distance = []
        for friend in friends:
            distance = self.distance_between_locations(self.hometown, friend.hometown)
            if distance is None:
                continue
            else:
                hometowns_by_distance.append({
                    'distance': distance,
                    'location': friend.hometown,
                    'person': friend
                })
        return sorted(hometowns_by_distance, key=lambda k: k['distance'])

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

    def add_relationship(self, person):
        relationship, created = Relationship.objects.get_or_create(from_person=person, to_person=self)
        return relationship

    def remove_relationship(self, person):
        Relationship.objects.filter(from_person=self, to_person=person).delete()

    def distance_between_locations(self, location_1, location_2):
        if isinstance(location_1, Location) and isinstance(location_2, Location):
            lat1 = location_1.latitude
            lng1 = location_1.longitude
            lat2 = location_2.latitude
            lng2 = location_2.longitude
            return geo.distance(lng1, lat1, lng2, lat2)
        else:
            return None


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
    type = models.CharField(max_length=1, choices=LOCATION_TYPES)
