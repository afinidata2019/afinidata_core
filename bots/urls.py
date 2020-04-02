from django.urls import path
from bots import views

app_name = 'bots'

urlpatterns = [
    path('', views.HomeView.as_view(), name='bot_list'),
    path('in_groups/', views.UserGroupBotsView.as_view(), name='bots_in_group_list'),
    path('new/', views.CreateBotView.as_view(), name='create_bot'),
    path('<int:bot_id>', views.BotView.as_view(), name='bot_detail'),
    path('<int:bot_id>/edit/', views.UpdateBotView.as_view(), name='edit_bot'),
    path('<int:bot_id>/delete/', views.DeleteBotView.as_view(), name='delete_bot')
]