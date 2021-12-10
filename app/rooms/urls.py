from django.urls import path
from rooms import views

urlpatterns = [
    path('', views.RoomList.as_view(), name='rooms')
]
