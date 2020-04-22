from app import service_views as views
from django.urls import path

app_name = 'app_services'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('create_instance/', views.CreateInstanceView.as_view(), name='create_instance'),
    path('get_instances/', views.GetInstancesView.as_view(), name='get_instances'),
    path('add_attribute/', views.AddAttributeToInstanceView.as_view(), name='add_attribute_to_instance'),
    path('areas/', views.AreaListView.as_view(), name='areas'),
    path('posts_by_area/', views.GetPostsByAreaView.as_view(), name='posts_by_area')
]