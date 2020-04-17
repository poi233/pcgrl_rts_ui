from django.urls import path

from . import views

app_name = "brush"

urlpatterns = [
    path('', views.index, name='index'),
    path('suggest', views.suggest, name='suggest'),
]
