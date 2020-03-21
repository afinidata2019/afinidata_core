from django.urls import path
from messenger_users import views

app_name = 'messenger_users'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('by_group/<str:group>/', views.ByGroupView.as_view(), name='by_group'),
    path('<int:id>/', views.UserView.as_view(), name='user'),
    path('<int:id>/data/<int:attribute_id>/edit/', views.EditAttributeView.as_view(), name='attribute_edit'),
    path('<int:id>/data/<int:attribute_id>/delete/', views.DeleteAttributeView.as_view(), name='attribute_delete')
]