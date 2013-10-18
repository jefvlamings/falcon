from django.db import models
from datetime import date


# Person
class Person(models.Model):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Unknown'),
    ]

    RELATIONSHIP_CHOICES = [
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
    ]

    fb_id = models.CharField(max_length=191, null=True, blank=True)
    relationships = models.ManyToManyField(
        'self', through='Relationship', symmetrical=False,
        related_name='related_to+'
    )
    access_token = models.TextField(null=True, blank=True)
    hash = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    relationship_status = models.CharField(
        max_length=1, choices=RELATIONSHIP_CHOICES
    )
    significant_other = models.CharField(max_length=30, null=True, blank=True)

    @property
    def name(self):
        name = self.first_name
        if self.middle_name is not '':
            name += ' ' + self.middle_name
        name += self.last_name
        return name

    @property
    def friends(self):
        return self.relationships.all()

    @property
    def posts(self):
        try:
            return Post.objects.filter(person=self)
        except Post.DoesNotExist:
            return None

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
    def progress(self):
        try:
            return Progress.objects.filter(person=self)
        except Progress.DoesNotExist:
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
            # raised when birth date is February 29 and the current year is not
            # a leap year
            birthday = self.birthday.replace(
                year=today.year,
                day=self.birthday.day-1
            )
        if birthday > today:
            return today.year - self.birthday.year - 1
        else:
            return today.year - self.birthday.year

    @property
    def friends_hometowns(self):
        """
        Returns a list of Locations for the hometowns of all Persons befriended
        with the current Person
        """
        locations = Location.objects.filter(
            person_id__in=self.friends,
            hometown_distance__isnull=False,
            type='H'
        )
        return locations

    @property
    def male_friends(self):
        """
        Returns a list of Persons who are male and befriended with the current
        Person
        """
        return self.friends.filter(gender='M')

    @property
    def male_friends_percentage(self):
        """
        Calculates the percentage of male friends relatively to the total
        amount of friends
        """
        number_of_male_friends = float(len(self.male_friends))
        number_of_friends = float(len(self.friends))
        percentage = (number_of_male_friends / number_of_friends) * 100
        return percentage

    @property
    def female_friends(self):
        """
        Returns a list of persons who are female and befriended with the current
        Person
        """
        return self.friends.filter(gender='F')

    @property
    def female_friends_percentage(self):
        """
        Calculates the percentage of female friends relatively to the total
        amount of friends
        """
        number_of_female_friends = float(len(self.female_friends))
        number_of_friends = float(len(self.friends))
        return number_of_female_friends / number_of_friends * 100

    def friends_by_mutual_friends(self, gender=None, order='ASC', limit=None):
        """
        Selects all friends by mutual friend count. It is possible to select by
        gender. Ordering allows selection of least mutual friends (ASC) or most
        mutual friends (DESC)
        """
        sql = """
            SELECT *
            FROM `fb_person`
               LEFT JOIN `fb_relationship`
                   ON ( `fb_person`.`id` = `fb_relationship`.`to_person_id` )
            WHERE  `fb_relationship`.`from_person_id` = %s
            """ % self.id
        if gender is not None:
            sql += """
                AND `fb_person`.`gender` = "%s"
                """ % gender
        sql += """
            ORDER  BY `fb_relationship`.`mutual_friend_count` %s
            """ % order
        if limit is not None:
            sql += """
                LIMIT %s
                """ % limit
        friends = Person.objects.raw(sql)
        return friends

    def mutual_friends_percentage(self, person):
        """
        Calculates the percentage of friends you have in common with a given
        person
        """
        mutual_friends = float(len(self.mutual_friends(person)))
        friends = float(len(self.friends()))
        return mutual_friends / friends * 100

    def friends_by_like_average(self, gender=None, order='ASC', limit=None):
        """
        Selects all friends and calculates the average like count for each
        friend. It is possible to select by gender. Ordering allows selection
        of lowest average like count (ASC) or highest average like count (DESC)
        """
        sql = """
            SELECT *, AVG(`like_count`) AS average
            FROM `fb_person`
                LEFT JOIN `fb_post` as a
                    ON ( `fb_person`.`id` = a.`person_id` )
                LEFT JOIN `fb_relationship`
                    ON ( `fb_person`.`id` = `fb_relationship`.`to_person_id` )
            WHERE `fb_relationship`.`from_person_id` = %s
            """ % self.id
        if gender is not None:
            sql += """
                AND `fb_person`.`gender` = "%s"
                """ % gender
        sql += """
            AND a.`like_count` IS NOT NULL
            GROUP BY `fb_person`.`id`
            ORDER BY average %s
        """ % order
        if limit is not None:
            sql += """
                LIMIT %s
                """ % limit

        friends = Person.objects.raw(sql)
        return friends

    def friends_by_post_count(self, gender=None, order='ASC', limit=None):
        """
        Selects all friends and calculates the number of posts for each
        friend. It is possible to select by gender. Ordering allows selection
        of least amount of posts (ASC) or most amount of posts (DESC)
        """
        sql = """
            SELECT *, COUNT(`like_count`) AS total
            FROM `fb_person`
                LEFT JOIN `fb_post` as a
                    ON ( `fb_person`.`id` = a.`person_id` )
                LEFT JOIN `fb_relationship`
                    ON ( `fb_person`.`id` = `fb_relationship`.`to_person_id` )
            WHERE `fb_relationship`.`from_person_id` = %s
            """ % self.id
        if gender is not None:
            sql += """
                AND `fb_person`.`gender` = "%s"
                """ % gender
        sql += """
            GROUP BY `fb_person`.`id`
            ORDER BY total %s
        """ % order
        if limit is not None:
            sql += """
                LIMIT %s
                """ % limit

        friends = Person.objects.raw(sql)
        return friends

    def add_relationship(self, person):
        """
        Creates a Relationship object linking the current person and a given
        person
        """
        relationship, created = Relationship.objects.get_or_create(
            from_person=person, to_person=self
        )
        return relationship

    def remove_relationship(self, person):
        """
        Removes the Relationship object linking the current person and a given
        person
        """
        Relationship.objects.filter(from_person=self, to_person=person).delete()


# Relationship
class Relationship(models.Model):
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')
    mutual_friend_count = models.IntegerField(max_length=30, null=True, blank=True)


# Location
class Location(models.Model):

    LOCATION_TYPES = [
        ('H', 'Hometown'),
        ('C', 'Current location'),
        ('P', 'Photo'),
        ('A', 'Album'),
    ]

    person = models.ForeignKey('Person')
    fb_id = models.CharField(max_length=191, null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    postal_code = models.CharField(max_length=191, null=True, blank=True)
    city = models.CharField(max_length=191, null=True, blank=True)
    country = models.CharField(max_length=191, null=True, blank=True)
    travel_distance = models.FloatField(null=True, blank=True)
    hometown_distance = models.FloatField(null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=LOCATION_TYPES)


# Progress
class Progress(models.Model):
    person = models.ForeignKey('Person')
    percentage = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


# Post
class Post(models.Model):

    POST_TYPES = [
        ('P', 'Photo'),
        ('V', 'Video'),
        ('L', 'Link'),
        ('S', 'Status'),
        ('C', 'Checkin'),
        ('Q', 'Question'),
        ('R', 'Review'),
        ('O', 'Offer'),
    ]

    fb_id = models.CharField(max_length=191, null=True, blank=True)
    person = models.ForeignKey('Person')
    message = models.TextField(null=True, blank=True)
    picture = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    like_count = models.IntegerField(max_length=30, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)



