from groups import messenger_users_views
from groups import codes_views
from groups import roles_views
from django.urls import path
from groups import views


app_name = 'groups'

urlpatterns = [
    path('', views.GroupListView.as_view(), name='groups'),
    path('<int:group_id>/', views.GroupView.as_view(), name='group'),
    path('<int:group_id>/add_user/', roles_views.CreateRoleView.as_view(), name='add_user_group'),
    path('<int:group_id>/add_messenger_user/', messenger_users_views.AddMessengerUserView.as_view(),
         name='add__messenger_user_group'),
    path('<int:group_id>/add_code/', codes_views.CreateCodeView.as_view(), name='add_code_group'),
    path('<int:group_id>/remove_assignation/<int:assignation_id>/',
         messenger_users_views.RemoveMessengerUserView.as_view(), name='remove_user_to_group'),
    path('add/', views.CreateGroupView.as_view(), name='add')
]
