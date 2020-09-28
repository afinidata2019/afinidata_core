from django.urls import path
from topics import views

app_name = 'topics'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='topic_list'),
    path('<int:topic_id>/', views.TopicDetailView.as_view(), name='topic_detail')
]
