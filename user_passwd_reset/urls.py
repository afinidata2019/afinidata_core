from django.urls import path
from . import views

app_name = 'user_passwd_reset'

urlpatterns = [
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
