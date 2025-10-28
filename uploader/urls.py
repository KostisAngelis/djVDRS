from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'uploader'
urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('export/<int:project_id>/', views.export_documents_by_project, name='export_by_project'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
