from django.urls import path
from . import views

app_name = 'vds'
urlpatterns = [
    path('', views.index, name='index'),
    path('project/<int:project_id>/details/',
         views.project_details, name='project_details'),
    path('document/<int:project_id>/list/',
         views.document_list, name='document_list'),
    path('document/<int:document_id>/details/',
         views.document_details, name='document_details'),
    path('revision/<int:revision_id>/edit/',
         views.revision_edit, name='revision_edit'),
    path('transmittal/<int:project_id>/list/',
        views.transmittal_list, name='transmittal_list'),
    path('transmittal/<int:transmittal_id>/details/',
         views.transmittal_details, name='transmittal_details'),
    path('transmittal/<int:project_id>/new/',
         views.transmittal_new, name='transmittal_new'),
    path('transmittal/add/',
         views.transmittal_add, name='transmittal_add'),    
    path('transmittal/<int:transmittal_id>/delete/',
         views.transmittal_delete, name='transmittal_delete'),
]