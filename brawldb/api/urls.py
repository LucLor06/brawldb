from django.urls import path
from . import views

urlpatterns = [
    path('combos/', views.CombosListView.as_view())
]