# about/urls.py
from . import views
from django.urls import path

app_name = 'about'

urlpatterns = [
    # Об авторе
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    # О технологиях
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
