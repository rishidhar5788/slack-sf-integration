from django.urls import path

from . import views

urlpatterns = [
	path('index/', views.admin_index, name='admin_index'),
	path('', views.index, name='index'),
	path('demo/', views.demo, name='demo')
]