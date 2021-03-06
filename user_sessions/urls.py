from user_sessions import views
from django.urls import path

app_name = 'sessions'

urlpatterns = [
    path('', views.SessionListView.as_view(), name='session_list'),
    path('test_session/', views.TestSessionView.as_view(), name='test_session'),
    path('interactions/', views.ReplyCorrectionListView.as_view(), name='nlu_correction_list'),
    path('interactions/<int:interaction_id>/', views.ReplyCorrectionView.as_view(), name='nlu_correction'),
    path('create/', views.SessionCreateView.as_view(), name='session_create'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('<int:session_id>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('<int:session_id>/add_field/', views.FieldCreateView.as_view(), name='field_create'),
    path('<int:session_id>/add_bot_session/', views.AddBotSessionView.as_view(), name='add_bot_session'),
    path('<int:session_id>/fields/<int:field_id>/delete/', views.FieldDeleteView.as_view(), name='field_delete'),
    path('<int:session_id>/fields/<int:field_id>/up/', views.FieldUpView.as_view(),
         name='field_up'),
    path('<int:session_id>/fields/<int:field_id>/down/', views.FieldDownView.as_view(),
         name='field_down'),
    path('<int:session_id>/fields/<int:field_id>/add_message/', views.MessageCreateView.as_view(),
         name='message_create'),
    path('<int:session_id>/fields/<int:field_id>/messages/<int:message_id>/edit/', views.MessageEditView.as_view(),
         name='message_edit'),
    path('<int:session_id>/fields/<int:field_id>/messages/<int:message_id>/delete/', views.MessageDeleteView.as_view(),
         name='message_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_userinput/', views.UserInputCreateView.as_view(),
         name='userinput_create'),
    path('<int:session_id>/fields/<int:field_id>/userinput/<int:userinput_id>/edit/', views.UserInputEditView.as_view(),
         name='userinput_edit'),
    path('<int:session_id>/fields/<int:field_id>/userinput/<int:userinput_id>/delete/', views.UserInputDeleteView.as_view(),
         name='userinput_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_reply/', views.ReplyCreateView.as_view(),
         name='reply_create'),
    path('<int:session_id>/fields/<int:field_id>/replies/<int:reply_id>/edit/', views.ReplyEditView.as_view(),
         name='reply_edit'),
    path('<int:session_id>/fields/<int:field_id>/replies/<int:reply_id>/delete/', views.ReplyDeleteView.as_view(),
         name='reply_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_button/', views.ButtonCreateView.as_view(),
         name='button_create'),
    path('<int:session_id>/fields/<int:field_id>/buttons/<int:button_id>/edit/', views.ButtonEditView.as_view(),
         name='button_edit'),
    path('<int:session_id>/fields/<int:field_id>/buttons/<int:button_id>/delete/', views.ButtonDeleteView.as_view(),
         name='button_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_setattribute/', views.SetAttributeCreateView.as_view(),
         name='setattribute_create'),
    path('<int:session_id>/fields/<int:field_id>/setattribute/<int:setattribute_id>/edit/',
         views.SetAttributeEditView.as_view(), name='setattribute_edit'),
    path('<int:session_id>/fields/<int:field_id>/setattribute/<int:setattribute_id>/delete/',
         views.SetAttributeDeleteView.as_view(), name='setattribute_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_condition/', views.ConditionCreateView.as_view(),
         name='condition_create'),
    path('<int:session_id>/fields/<int:field_id>/condition/<int:condition_id>/edit/',
         views.ConditionEditView.as_view(), name='condition_edit'),
    path('<int:session_id>/fields/<int:field_id>/condition/<int:condition_id>/delete/',
         views.ConditionDeleteView.as_view(), name='condition_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_block/', views.RedirectBlockCreateView.as_view(),
         name='block_create'),
    path('<int:session_id>/fields/<int:field_id>/blocks/<int:block_id>/edit/', views.RedirectBlockEditView.as_view(),
         name='block_edit'),
    path('<int:session_id>/fields/<int:field_id>/blocks/<int:block_id>/delete/',
         views.RedirectBlockDeleteView.as_view(), name='block_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_service/', views.ServiceCreateView.as_view(),
         name='service_create'),
    path('<int:session_id>/fields/<int:field_id>/services/<int:service_id>/edit/', views.ServiceEditView.as_view(),
         name='service_edit'),
    path('<int:session_id>/fields/<int:field_id>/services/<int:service_id>/delete/',
         views.ServiceDeleteView.as_view(), name='service_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_serviceparam/', views.ServiceParamCreateView.as_view(),
         name='serviceparam_create'),
    path('<int:session_id>/fields/<int:field_id>/serviceparams/<int:serviceparam_id>/edit/',
         views.ServiceParamEditView.as_view(), name='serviceparam_edit'),
    path('<int:session_id>/fields/<int:field_id>/serviceparams/<int:serviceparam_id>/delete/',
         views.ServiceParamDeleteView.as_view(), name='serviceparam_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_redirectsession/', views.RedirectSessionCreateView.as_view(),
         name='redirectsession_create'),
    path('<int:session_id>/fields/<int:field_id>/redirectsession/<int:redirectsession_id>/edit/',
         views.RedirectSessionEditView.as_view(), name='redirectsession_edit'),
    path('<int:session_id>/fields/<int:field_id>/redirectsession/<int:redirectsession_id>/delete/',
         views.RedirectSessionDeleteView.as_view(), name='redirectsession_delete'),
     path('fields/<int:pk>/', views.FieldsData.as_view(), name="api_fields_data")
]
