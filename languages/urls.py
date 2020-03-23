from django.urls import path
from languages import views

app_name = 'languages'

urlpatterns = [
    path('', views.LanguageListView.as_view(), name='language_list'),
    path('<int:language_id>/', views.LanguageView.as_view(), name='language_detail'),
    path('new_language/', views.LanguageCreateView.as_view(), name='language_create'),
    path('<int:language_id>/edit/', views.LanguageEditView.as_view(), name='language_edit'),
    path('<int:language_id>/language_codes/', views.LanguageCodeListView.as_view(), name='language_code_list'),
    path('<int:language_id>/new_language_code/', views.LanguageCodeCreateView.as_view(), name='language_code_create'),
    path('<int:language_id>/language_code/<int:language_code_id>/', views.LanguageCodeView.as_view(),
         name='language_code'),
    path('<int:language_id>/language_code/<int:language_code_id>/edit/', views.LanguageCodeEditView.as_view(),
         name='language_code_edit'),
    path('<int:language_id>/language_code/<int:language_code_id>/delete/', views.LanguageCodeDeleteView.as_view(),
         name='language_code_delete')
]
