"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Перенаправляет веб запросы на ursl.py приложения posts
    path('', include('posts.urls', namespace='posts')),
    # Перенаправляет веб запросы на ursl.py приложения users
    path('auth/', include('users.urls', namespace='users')),
    # Перенаправляет веб запросы на ursl.py приложения about
    path('about/', include('about.urls', namespace='about')),
    path('', include('django.contrib.auth.urls')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
