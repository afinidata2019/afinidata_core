from django.urls import path
from programs import views

app_name = 'programs'

urlpatterns = [
    path('', views.ProgramListView.as_view(), name='program_list'),
    path('<int:program_id>/', views.ProgramDetailView.as_view(), name='program_detail'),
    path('<int:program_id>/edit/', views.ProgramUpdateView.as_view(), name='program_edit'),
    path('<int:program_id>/delete/', views.ProgramDeleteView.as_view(), name='program_delete'),
    path('new_program/', views.ProgramCreateView.as_view(), name='program_create')
]
