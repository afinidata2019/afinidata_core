from django.urls import path
from messenger_users import views

app_name = 'messenger_users'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('create_user_afini/', views.CreateAfinidataUser.as_view(), name='create_afini_user'),
    path('<int:id>/', views.UserView.as_view(), name='user'),
    path('<int:id>/delete/', views.DeleteUserView.as_view(), name='delete'),
    path('<int:id>/interactions/', views.UserInteractionsView.as_view(), name='user_interactions'),
    path('<int:id>/bot_interactions/', views.UserBotInteractionListView.as_view(), name='user_bot_interactions'),
    path('<int:id>/post_interactions/', views.UserPostInteractionListView.as_view(), name='user_post_interactions'),
    path('<int:id>/article_interactions/', views.UserArticleInteractionListView.as_view(),
         name='user_article_interactions'),
    path('<int:id>/session_interactions/', views.UserSessionInteractionListView.as_view(),
         name='user_session_interactions'),
    path('<int:user_id>/want_add_child/', views.WantAddChildView.as_view(), name='want_add_child'),
    path('<int:user_id>/add_child/', views.AddChildView.as_view(), name='add_child'),
    path('<int:user_id>/data/', views.UserDataListView.as_view(), name='user_data_list'),
    path('<int:user_id>/last_data/', views.UserLastDataListView.as_view(), name='user_last_data_list'),
    path('<int:user_id>/create_data/', views.UserDataCreateView.as_view(), name='user_create_data'),
    path('<int:user_id>/edit_data/<int:userdata_id>/', views.UserDataUpdateView.as_view(), name='user_edit_data'),
    path('<int:user_id>/delete_data/<int:userdata_id>/', views.UserDataDeleteView.as_view(), name='user_delete_data'),
    path('<int:user_id>/add_initial_data/', views.AddUserInitialData.as_view(), name='user_initial_data')
]