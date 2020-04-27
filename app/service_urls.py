from app import service_views as views
from django.urls import path

app_name = 'app_services'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('anon_signup/', views.AnonSignUpView.as_view(), name='anon_signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('create_instance/', views.CreateInstanceView.as_view(), name='create_instance'),
    path('get_instances/', views.GetInstancesView.as_view(), name='get_instances'),
    path('add_attribute/', views.AddAttributeToInstanceView.as_view(), name='add_attribute_to_instance'),
    path('areas/', views.AreaListView.as_view(), name='areas'),
    path('posts_by_area/', views.GetPostsByAreaView.as_view(), name='posts_by_area'),
    path('get_post/', views.GetPostView.as_view(), name='get_post'),
    path('exchange_code/', views.ExchangeCodeView.as_view(), name='exchange_code'),
    path('verify_groups/', views.VerifyGroups.as_view(), name='verify_group'),
    path('verify_attribute/', views.VerifyAttributeView.as_view(), name='verify_attribute')
]