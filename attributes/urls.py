from django.urls import path
from attributes import views

app_name = 'attributes'

urlpatterns = [
    path('', views.AttributesView.as_view(), name="attribute_list"),
    path('create_attribute/', views.NewAttributeView.as_view(), name="create_attribute"),
    path('<int:attribute_id>/', views.AttributeView.as_view(), name="attribute_detail"),
    path('<int:attribute_id>/edit/', views.EditAttributeView.as_view(), name='edit_attribute'),
    path('<int:attribute_id>/delete/', views.DeleteAttributeView.as_view(), name='delete_attribute')
]
