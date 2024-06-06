from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import User, Favorites, Tabelog, FinalScore, Region
from .forms import SignUpForm

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.http import require_GET

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.http import require_GET

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.http import require_GET

def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def mypage(request):
    favorites = Favorites.objects.filter(user=request.user)
    return render(request, 'mypage.html', {'favorites': favorites})

def search(request):
    stations = Region.objects.values_list('station', flat=True).distinct()
    return render(request, 'search.html', {'stations': stations})

def restaurants_by_station(request, station):
    restaurants = Tabelog.objects.filter(station__station=station).select_related('google').prefetch_related('final_score')
    sort = request.GET.get('sort', 'new_score')
    if sort == 'new_score_asc':
        restaurants = restaurants.order_by('final_score__new_score')
    elif sort == 'new_score_desc':
        restaurants = restaurants.order_by('-final_score__new_score')
    paginator = Paginator(restaurants, 20)
    page = request.GET.get('page')
    restaurants = paginator.get_page(page)
    return render(request, 'restaurants_by_station.html', {'restaurants': restaurants, 'station': station, 'sort': sort})

@login_required
def add_favorite(request, tabelog_id):
    tabelog = Tabelog.objects.get(id=tabelog_id)
    Favorites.objects.create(user=request.user, tabelog=tabelog)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_favorite(request, tabelog_id):
    tabelog = Tabelog.objects.get(id=tabelog_id)
    favorite = Favorites.objects.filter(user=request.user, tabelog=tabelog)
    if favorite.exists():
        favorite.delete()
    return redirect(request.META.get('HTTP_REFERER', 'mypage'))
