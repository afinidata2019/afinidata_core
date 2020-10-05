from django.urls import path
from programs import views

app_name = 'programs'

urlpatterns = [
    path('', views.ProgramListView.as_view(), name='program_list'),
    path('new_program/', views.ProgramCreateView.as_view(), name='program_create'),
    path('new_group_program/', views.CreateGroupProgramView.as_view(), name='group_program_create'),
    path('<int:program_id>/', views.ProgramDetailView.as_view(), name='program_detail'),
    path('<int:program_id>/content/', views.ProgramDetailContentView.as_view(), name='program_content_detail'),
    path('<int:program_id>/set_areas/', views.ProgramSetAreasView.as_view(), name='program_set_areas'),
    path('<int:program_id>/edit/', views.ProgramUpdateView.as_view(), name='program_edit'),
    path('<int:program_id>/delete/', views.ProgramDeleteView.as_view(), name='program_delete'),
    path('<int:program_id>/levels/', views.LevelListView.as_view(), name='level_list'),
    path('<int:program_id>/new_level/', views.LevelCreateView.as_view(), name='level_create'),
    path('<int:program_id>/level/<int:level_id>/', views.LevelDetailView.as_view(), name='level_detail'),
    path('<int:program_id>/level/<int:level_id>/edit/', views.LevelUpdateView.as_view(), name='level_edit'),
    path('<int:program_id>/level/<int:level_id>/delete/', views.LevelDeleteView.as_view(), name='level_delete'),
    path('<int:program_id>/level/<int:level_id>/add_milestone/', views.LevelMilestoneCreateView.as_view(),
         name='add_level_milestone')
]
