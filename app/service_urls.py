from app import service_views as views
from django.urls import path

app_name = 'app_services'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='login')
]