from django.urls import path
from . import views

app_name = 'user_passwd_reset'

urlpatterns = [
    path('', views.PasswordResetView.as_view(), name='password_reset'),
    path('done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
