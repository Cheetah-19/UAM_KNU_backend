from django.urls import path
from .views import *

urlpatterns = [
    path('', RegisterView.as_view(), name='user_register'),
    path('/auth', AuthView.as_view(), name='user_auth'),
    path('/info', InfoView.as_view(), name='user_info'),
    path('/history', HistoryView.as_view(), name='user_history'),
]
