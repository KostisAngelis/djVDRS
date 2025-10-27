from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from uploader import views as uploader_views

from . import views

app_name = 'uploader'
urlpatterns = [
    path('', uploader_views.UploadView.as_view(), name='fileupload'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
