from django.urls import path
from messenger_users import views

app_name = 'messenger_users'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('<int:id>/', views.UserView.as_view(), name='user'),
    path('<int:user_id>/data/', views.UserDataListView.as_view(), name='user_data_list')
]