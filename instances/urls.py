from django.urls import path
from instances import views

app_name = 'instances'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('new/', views.NewInstanceView.as_view(), name='new'),
    path('<int:id>/', views.InstanceView.as_view(), name='instance'),
    path('<int:id>/edit/', views.EditInstanceView.as_view(), name='edit'),
    path('<int:id>/delete/', views.DeleteInstanceView.as_view(), name='delete'),
    path('<int:instance_id>/add_attribute/', views.AddAttributeToInstanceView.as_view(), name='add_instance_attribute'),
    path('<int:instance_id>/edit_attribute/<int:attribute_id>/', views.AttributeValueEditView.as_view(),
         name='edit_instance_attribute')
]