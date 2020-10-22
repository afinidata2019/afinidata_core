from django.urls import path
from utilities import views

app_name = 'utilities'

urlpatterns = [
    path('translate/', views.TranslateView.as_view(), name='translate'),
    path('group_assignations/', views.GroupAssignationsView.as_view(), name='group_assignations'),
    path('ficha_instancia/', views.GroupInstanceCardView.as_view(), name='ficha_instancia'),
    path('create_program/', views.CreateProgramDemoView.as_view(), name='create_program'),
    path('new_program/', views.NewProgramDemoView.as_view(), name='new_program'),
    path('edit_level/', views.EditLevelDemoView.as_view(), name='edit_level'),
    path('cognitive_example/', views.CognitiveExampleView.as_view(), name='cognitive_example')
]
