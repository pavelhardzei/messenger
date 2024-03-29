from django.urls import path, re_path
from users import views

urlpatterns = [
    path('', views.UserList.as_view(), name='user_list'),
    path('signup/', views.UserSignUp.as_view(), name='signup'),
    path('signin/', views.UserSignIn.as_view(), name='signin'),
    path('verify/', views.EmailVerification.as_view(), name='email_verification'),
    path('resend/', views.ResendVerification.as_view(), name='resend_verifiaction'),
    path('totp/', views.TurnTOTP.as_view(), name='totp'),
    path('online/', views.UsersOnline.as_view(), name='users_online'),
    re_path(r'^(?P<pk>(\d+|me))/$', views.UserDetail.as_view(), name='user_detail'),
    re_path(r'^change_pwd/(?P<pk>(\d+|me))/$', views.ChangePassword.as_view(), name='user_change_pwd'),
    path('sociallogin/', views.GoogleLogin.as_view(), name='sociallogin')
]
