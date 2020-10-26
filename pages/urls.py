from django.urls import path
from pages import views

app_name = 'pages'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
