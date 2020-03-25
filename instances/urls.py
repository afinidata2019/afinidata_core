from django.urls import path
from instances import views

app_name = 'instances'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('new/', views.NewInstanceView.as_view(), name='new'),
    path('<int:id>/', views.InstanceView.as_view(), name='instance'),
    path('<int:id>/edit/', views.EditInstanceView.as_view(), name='edit'),
    path('<int:id>/delete/', views.DeleteInstanceView.as_view(), name='delete'),
    path('<int:id>/add_attribute/', views.AddAttributeToInstance.as_view(), name="add_attribute"),
    path('<int:id>/add_section/', views.InstanceSectionView.as_view(), name="add_section"),
    path('<int:id>/evaluator/', views.Evaluator.as_view(), name="evaluator"),
    path('<int:id>/up/', views.up_instance, name='up'),
    path('<int:id>/get_activity/', views.GetActivityView.as_view(), name='get_activity')
]