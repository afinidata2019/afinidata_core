from django.urls import path
from entities import views

app_name = 'entities'

urlpatterns = [
    path('', views.HomeView.as_view(), name='entity_list'),
    path('new/', views.NewEntityView.as_view(), name='create_entity'),
    path('<int:entity_id>/', views.EntityView.as_view(), name='entity_detail'),
    path('<int:entity_id>/edit/', views.EditEntityView.as_view(), name='edit_entity'),
    path('<int:entity_id>/delete/', views.DeleteEntityView.as_view(), name='delete_entity'),
    path('<int:entity_id>/add_attribute/', views.AddAttributeToEntityView.as_view(), name='add_attribute_to_entity')
]
