from django.urls import path
from rooms import views

urlpatterns = [
    path('', views.RoomList.as_view(), name='rooms'),
    path('<int:pk>/', views.RoomDetail.as_view(), name='room_detail'),
    path('<int:pk>/enter/', views.EnterRoom.as_view(), name='room_enter'),
    path('<int:pk>/leave/', views.LeaveRoom.as_view(), name='leave_room'),
    path('<int:room_pk>/user/<int:user_pk>/', views.RemoveUser.as_view(), name='remove_user'),
    path('<int:room_pk>/user/<int:user_pk>/role/', views.SetRole.as_view(), name='set_role'),
    path('find/', views.RoomFinding.as_view(), name='find_room'),
    path('invitation/', views.MakeInvitation.as_view(), name='make_invitation'),
    path('invitation/<uuid:uuid4>/', views.AcceptInvitation.as_view(), name='accept_invitation')
]
