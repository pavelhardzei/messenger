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
    re_path(r'^invitation/(?P<uuid4>([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}'
            r'-[0-9A-Fa-f]{12}))/$', views.AcceptInvitation.as_view(), name='accept_invitation')
]
