from django.urls import path
from base import views


urlpatterns = [
    path('health/', views.health, name='health')
]
