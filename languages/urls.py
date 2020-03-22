from django.urls import path
from languages import views

app_name = 'languages'

urlpatterns = [
    path('', views.LanguageListView.as_view(), name='language_list'),
    path('new_language/', views.LanguageCreateView.as_view(), name='language_create'),
    path('<int:language_id>/', views.LanguageView.as_view(), name='language_detail')
]
