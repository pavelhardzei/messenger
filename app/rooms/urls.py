from django.urls import path, re_path
from rooms import views

urlpatterns = [
    path('', views.RoomList.as_view(), name='rooms'),
    path('<int:pk>/', views.RoomDetail.as_view(), name='room_detail'),
    path('enter/', views.EnterRoom.as_view(), name='room_enter'),
    path('leave/', views.LeaveRoom.as_view(), name='leave_room'),
    path('remove/', views.RemoveUser.as_view(), name='remove_user'),
    path('setrole/', views.SetRole.as_view(), name='set_role'),
    path('invitation/', views.MakeInvitation.as_view(), name='make_invitation'),
    path('invitation/<uuid:uuid4>/', views.AcceptInvitation.as_view(), name='accept_invitation')
]
