from base import views
from django.urls import path

urlpatterns = [
    path('health/', views.health, name='health')
]
