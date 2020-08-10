from user_sessions import views
from django.urls import path

app_name = 'sessions'

urlpatterns = [
    path('', views.SessionListView.as_view(), name='session_list'),
    path('create/', views.SessionCreateView.as_view(), name='session_create'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('<int:session_id>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('<int:session_id>/add_field/', views.FieldCreateView.as_view(), name='field_create'),
    path('<int:session_id>/field/<int:field_id>/add_message/', views.MessageCreateView.as_view(),
         name='message_create'),
    path('<int:session_id>/field/<int:field_id>/messages/<int:message_id>/edit/', views.MessageEditView.as_view(),
         name='message_edit'),
    path('<int:session_id>/field/<int:field_id>/messages/<int:message_id>/delete/', views.MessageDeleteView.as_view(),
         name='message_delete')
]
