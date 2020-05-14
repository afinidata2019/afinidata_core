from django.urls import path
from messenger_users import views

app_name = 'messenger_users'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('<int:id>/', views.UserView.as_view(), name='user'),
    path('<int:user_id>/data/', views.UserDataListView.as_view(), name='user_data_list'),
    path('<int:user_id>/create_data/', views.UserDataCreateView.as_view(), name='user_create_data'),
    path('<int:user_id>/edit_data/<int:userdata_id>/', views.UserDataUpdateView.as_view(), name='user_edit_data'),
    path('<int:user_id>/delete_data/<int:userdata_id>/', views.UserDataDeleteView.as_view(), name='user_delete_data')
]