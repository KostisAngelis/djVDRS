import csv, io

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.core.files.storage import default_storage
from .forms import UploadCSVForm
from vds.models import Document
from .admin import DocumentResource
from tablib import Dataset  # used by django-import-export

def export_documents_by_project(request, project_id):
    resource = DocumentResource()
    queryset = Document.objects.filter(project_id=project_id)
    dataset = resource.export(queryset)

    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="document_list.csv"'
    return response


def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']

            # Optional: save file temporarily
            # If you do, you need to change how you read from csv_file below
            # path = default_storage.save('uploads/' + csv_file.name, csv_file)

            # Read and parse CSV with import-export
            dataset = Dataset().load(csv_file.read().decode('utf-8'))

            document_resource = DocumentResource()
            result = document_resource.import_data(dataset, dry_run=True)  # check for errors first


            if not result.has_errors():
                document_resource.import_data(dataset, dry_run=False)  # actually save
                messages.success(request, "Data imported successfully!")
                return redirect('uploader:upload_csv')
            else:
                messages.error(request, "Errors occurred while importing data.")
                return render(request, 'uploader/upload_form.html', {
                    'form': form,
                    'errors': result.row_errors(),
                })
    else:
        form = UploadCSVForm()

    return render(request, 'uploader/upload_form.html', {'form': form})
