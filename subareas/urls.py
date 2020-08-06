from django.urls import path
from areas import views

app_name = 'areas'

urlpatterns = [
    path('', views.HomeView.as_view(), name='area_list'),
    path('new/', views.NewAreaView.as_view(), name='create_area'),
    path('<int:area_id>/', views.AreaView.as_view(), name='area_detail'),
    path('<int:area_id>/edit/', views.EditAreaView.as_view(), name='edit_area'),
    path('<int:area_id>/delete/', views.DeleteAreaView.as_view(), name='delete_area')
]
