from django.urls import path
from room_messages import views

urlpatterns = [
    path('', views.MessageCreate.as_view(), name='message_create'),
    path('<int:pk>/', views.MessageDetail.as_view(), name='message_detail')
]
