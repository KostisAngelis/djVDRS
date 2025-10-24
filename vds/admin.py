from django.contrib import admin

from .models import Project, Document, Transmittal, Revision

# Register your models here.
admin.site.register(Project)
admin.site.register(Document)
admin.site.register(Transmittal)
admin.site.register(Revision)
