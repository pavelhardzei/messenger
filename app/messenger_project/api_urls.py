from django.urls import include, path

urlpatterns = [
    path('base/', include('base.urls')),
    path('user/', include('users.urls'))
]
