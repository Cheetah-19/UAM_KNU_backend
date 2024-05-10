from django.urls import path
from .views import *

urlpatterns = [
    path('', OptimizationView.as_view(), name='optimization')
]