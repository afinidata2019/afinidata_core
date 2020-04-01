from django.urls import path
from chatfuel import views

app_name = 'chatfuel'

urlpatterns = [
    path('create_messenger_user_data/', views.CreateMessengerUserDataView.as_view(), name='create_messenger_user_data'),
    path('create_instance_attribute/', views.CreateInstanceAttributeView.as_view(), name='create_instance_attribute'),
    path('get_instance_attribute/', views.GetInstanceAttributeView.as_view(), name='get_instance_attribute'),
    path('change_instance_name/', views.ChangeInstanceNameView.as_view(), name='change_instance_name'),
    path('create_instance_interaction_view/', views.CreateInstanceInteractionView.as_view(),
         name='create_instance_interaction_view'),
    path('create_messenger_user/', views.CreateMessengerUserView.as_view(), name='create_messenger_user'),
    path('create_instance/', views.create_instance, name='new_instance'),
    path('get_instances/', views.GetInstancesByUserView.as_view(), name='get_instances'),
    path('exchange_code/', views.ExchangeCodeView.as_view(), name='exchange_code'),
    path('verify_code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('get_favorite_child/', views.GetFavoriteChildView.as_view(), name='get_favorite_child'),
    path('get_last_child/', views.GetLastChildView.as_view(), name='get_last_child')
]