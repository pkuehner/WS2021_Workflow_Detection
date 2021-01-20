from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('workflow', views.workflow, name='workflow'),
    path('bpmn', views.bpmn, name='bpmn'),
    path('pn', views.pn, name='pn')
]
