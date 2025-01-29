from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
