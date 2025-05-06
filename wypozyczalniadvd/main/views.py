from django.shortcuts import render, redirect
from .models import Katalog, Wypozyczenia
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


def index(request):
    template_data = {}
    template_data['formularz_rejestracji'] = CustomUserCreationForm()
    template_data['formularz_logowania'] = AuthenticationForm()
    template_data['uzytkownik'] = request.user

    pole_sortowania = request.GET.get('sortowanie', 'nazwa')
    kolejnosc = request.GET.get('kolejnosc', 'asc')
    template_data['kolejnosc'] = kolejnosc
    template_data['pole_sortowania'] = pole_sortowania

    if kolejnosc == 'asc':
        sortowanie = pole_sortowania
    else:
        sortowanie = f"-{pole_sortowania}"
    template_data['filmy'] = Katalog.objects.all().order_by(sortowanie)

    if request.user.is_authenticated:
        wypozyczone_katalogi = Katalog.objects.filter(wypozyczenia__uzytkownik = request.user).order_by('nazwa').distinct()
        wypozyczone_id = wypozyczone_katalogi.values_list('id', flat=True)

        template_data['wypozyczone_katalogi'] = wypozyczone_katalogi
        template_data['wypozyczenia_id'] = wypozyczone_id

    if request.method == 'POST':
        if request.POST.get('rejestracja') is not None:
            formularz_rejestracji = CustomUserCreationForm(request.POST)
            if formularz_rejestracji.is_valid():
                user = formularz_rejestracji.save()
                template_data['powodzenie_rejestracji'] = True
                login(request, user)
                return redirect('index')
            else:
                template_data['formularz_rejestracji'] = formularz_rejestracji

        elif request.POST.get('login') is not None:
            formularz_logowania = AuthenticationForm(data=request.POST)
            if formularz_logowania.is_valid():
                user = formularz_logowania.get_user()
                login(request, user)
                return redirect('index')
            else:
                template_data['formularz_logowania'] = formularz_logowania

        elif request.POST.get('wyloguj') is not None:
            logout(request)
            return redirect('index')
        
        elif request.POST.get('wypozycz') is not None:
            film_id = request.POST.get('id')
            try:
                film = Katalog.objects.get(id=film_id)
            except Katalog.DoesNotExist:
                film = None

            if film and film.ilosc > 0:
                wypozyczony = Wypozyczenia.objects.filter(katalog=film, uzytkownik=request.user).exists()
                if not wypozyczony:
                    Wypozyczenia.objects.create(katalog=film, uzytkownik=request.user)
                    film.ilosc -= 1
                    film.save()
            return redirect('index')

        elif request.POST.get('zwroc') is not None:
            film_id = request.POST.get('id')
            try:
                film = Katalog.objects.get(id=film_id)
            except Katalog.DoesNotExist:
                film = None

            if film:
                wypozyczenie = Wypozyczenia.objects.filter(katalog=film, uzytkownik=request.user).first()
                if wypozyczenie:
                    wypozyczenie.delete()
                    film.ilosc += 1
                    film.save()
            return redirect('index')

    
    return render(request, 'main/index.html', {
        "template_data": template_data
    })
