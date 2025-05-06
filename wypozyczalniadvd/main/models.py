from django.db import models
from django.contrib.auth.models import User    

class Katalog(models.Model):
    nazwa = models.CharField(max_length=100)
    rezyseria = models.CharField(max_length=100)
    gatunek = models.CharField(max_length=100)
    ilosc = models.IntegerField()

    def __str__(self):
        return self.nazwa

class Wypozyczenia(models.Model):
    katalog = models.ForeignKey(Katalog, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.uzytkownik.username} wypożyczył {self.katalog}"