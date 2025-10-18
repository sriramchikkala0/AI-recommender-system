# reco/urls.py
from django.urls import path
from .views import recommend_view

urlpatterns = [
    path('recommendations/<int:user_id>/', recommend_view, name='recommend'),
]