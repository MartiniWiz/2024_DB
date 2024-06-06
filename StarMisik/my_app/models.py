from django.db import models

# Create your models here.

class Region(models.Model):
    station = models.CharField(max_length=100, primary_key=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.station

class Tabelog(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    station = models.ForeignKey(Region, on_delete=models.CASCADE)
    menu = models.CharField(max_length=200)
    score = models.FloatField()
    num_reviews = models.IntegerField()

    def __str__(self):
        return self.name

class Google(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    google_score = models.FloatField()
    num_reviews_google = models.IntegerField()

    def __str__(self):
        return self.name

class FinalScore(models.Model):
    address = models.ForeignKey(Tabelog, on_delete=models.CASCADE)
    new_score = models.FloatField()

    def __str__(self):
        return f"{self.address.name} - {self.new_score}"

class User(models.Model):
    id = models.AutoField(primary_key=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)

    def __str__(self):
        return str(self.id)

class Favorites(models.Model):
    address = models.ForeignKey(Tabelog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.id} - {self.address.name}"    