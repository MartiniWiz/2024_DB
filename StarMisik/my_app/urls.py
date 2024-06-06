from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('search/', views.search, name='search'),
    path('station/<str:station>/', views.restaurants_by_station, name='restaurants_by_station'),
    path('add_favorite/<int:tabelog_id>/', views.add_favorite, name='add_favorite'),
    path('remove_favorite/<int:tabelog_id>/', views.remove_favorite, name='remove_favorite'),
]
