from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'uploader'
urlpatterns = [
    path('project/<int:project_id>/export/', views.export_project_json, name='export_project_json'),
    path('document/import_list/', views.upload_csv, name='upload_csv'),
    path('document/<int:project_id>/export_list/', views.export_documents_by_project, name='export_by_project'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
