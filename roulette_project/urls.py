from django.urls import path
from django.contrib.auth import views as auth_views
from roulette_app import views

urlpatterns = [
    path('', views.frontend, name='frontend'),
    path('backend/', views.backend, name='backend'),
    path('api/draw/', views.api_draw, name='api_draw'),
    path('api/new-activity/', views.api_new_activity, name='api_new_activity'),
    path('api/delete-activity/', views.api_delete_activity, name='api_delete_activity'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
