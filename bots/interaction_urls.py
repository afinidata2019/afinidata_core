from django.urls import path
from bots import views

app_name = 'bot_interactions'

urlpatterns = [
    path('', views.BotInteractionListView.as_view(), name='bot_interaction_list'),
    path('create/', views.CreateBotInteractionView.as_view(), name='bot_interaction_create'),
    path('<int:interaction_id>/', views.BotInteractionDetailView.as_view(), name='bot_interaction_detail'),
    path('<int:interaction_id>/edit/', views.UpdateBotInteractionView.as_view(), name='bot_interaction_edit')
]
