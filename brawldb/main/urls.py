from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('combos/add/', views.combos_add, name='combos_add'),
    path('combos/', views.combos, name='combos'),
    path('combos/<pk>/', views.combo, name='combo'),
    path('patches/', views.patches, name='patches'),
    path('terminology/', views.terminology, name='terminology')
]