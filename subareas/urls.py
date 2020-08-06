from django.urls import path
from subareas import views

app_name = 'subareas'

urlpatterns = [
    path('', views.HomeView.as_view(), name='subarea_list'),
    path('new/', views.NewSubareaView.as_view(), name='create_subarea'),
    path('<int:subarea_id>/', views.SubareaView.as_view(), name='subarea_detail'),
    path('<int:subarea_id>/edit/', views.EditSubareaView.as_view(), name='edit_subarea'),
    path('<int:subarea_id>/delete/', views.DeleteSubareaView.as_view(), name='delete_subarea')
]
