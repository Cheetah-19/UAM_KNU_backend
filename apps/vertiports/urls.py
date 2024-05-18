from django.urls import path
from .views import *

urlpatterns = [
    path('', VertiportView.as_view(), name='vertiport_management'),
    path('/<str:name>', VertiportView.as_view(), name='vertiport_deletion'),
]
