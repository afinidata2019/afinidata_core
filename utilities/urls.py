from django.urls import path
from utilities import views

app_name = 'utilities'

urlpatterns = [
    path('translate/', views.TranslateView.as_view(), name='translate')
]
