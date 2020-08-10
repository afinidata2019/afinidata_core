from user_sessions import views
from django.urls import path

app_name = 'sessions'

urlpatterns = [
    path('', views.SessionListView.as_view(), name='session_list'),
    path('create/', views.SessionCreateView.as_view(), name='session_create'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('<int:session_id>/delete/', views.SessionDeleteView.as_view(), name='session_delete')
]
