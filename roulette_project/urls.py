from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from roulette_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.frontend, name='frontend'),
    path('backend/', views.backend, name='backend'),
    path('api/draw/', views.api_draw, name='api_draw'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
