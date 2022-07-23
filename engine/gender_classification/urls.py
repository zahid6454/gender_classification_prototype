from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('initializer', views.initializer, name="initializer"),
    path('prediction', views.prediction, name="prediction"),
    path('download/<file_path>', views.download, name='download'),
]

