from django.urls import path, re_path
from users import views

urlpatterns = [
    path('', views.UserList.as_view(), name='user_list'),
    path('signup/', views.UserSignUp.as_view(), name='signup'),
    path('signin/', views.UserSignIn.as_view(), name='signin'),
    re_path(r'^(?P<pk>(\d+|me))/$', views.UserDetail.as_view(), name='user_detail'),
    re_path(r'^change_pwd/(?P<pk>(\d+|me))/$', views.ChangePassword.as_view(), name='user_change_pwd')
]
