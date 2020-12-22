from django.urls import path
from conversations import views

app_name = 'conversations'

urlpatterns = [
    path('conversation_workflow/', views.ConversationWorkflow.as_view(), name='conversation_workflow')
]
