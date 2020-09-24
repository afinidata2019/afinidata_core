from django.urls import path
from utilities import views

app_name = 'utilities'

urlpatterns = [
    path('translate/', views.TranslateView.as_view(), name='translate'),
    path('group_assignations/', views.GroupAssignationsView.as_view(), name='group_assignations')
]
