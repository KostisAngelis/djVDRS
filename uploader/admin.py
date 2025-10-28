from django.contrib import admin
from import_export import resources

from vds.models import Document

# Register your models here.
class DocumentResource(resources.ModelResource):
    # Refer to
    # https://django-import-export.readthedocs.io/en/latest/getting_started.html

    class Meta:
        model = Document
        exclude = ('id',)
        import_id_fields = ('document_number',)
        '''
        fields = (
            'project', 'title', 'vds_status', 'stub', 'discipline',
            'document_number', 'client_number', 'supplier_number',
            'revision_number', 'required_by', 'first_issue', 'latest_issue',
            'next_due', 'notes', 'penalty', 'milestone', 'priority',
        )
        '''
