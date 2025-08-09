from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.AudiobookListView.as_view(), name='audiobook-list'),
    path('audiobook/<int:pk>/edit/', views.AudiobookUpdateView.as_view(), name='audiobook-edit'),
] 