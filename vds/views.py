from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404

from .models import Project, Document, Revision, Transmittal



# Create your views here.
def index(request):
    '''
    Home page of site.
    Displays a list of the latest projects set up.
    Soon it will also display the latest transmittals across projects or 
    for the active project.
    A couple of buttons will be added, for creating a new project or a new
    transmittal, as well as de-activating a project.
    A project cannot formally be deleted.
    '''
    latest_project_list = Project.objects.order_by("-wa_number")[:5]
    recent_transmittals = Transmittal.objects.order_by('-date_sent')[:10]
    context = {
        'latest_project_list': latest_project_list,
        'recent_transmittals': recent_transmittals,
    }
    return render(request,'vds/index.html',context)


def vds(request, project_id):
    '''
    View function for main access page of site, displaying the document list
    for a specific WA.
    It will display the main project information at the top and the main fields
    from the VDS for the selected project.
    For any selected document, it will display the full details and its revision history.
    '''
    return HttpResponse("Hello, world. You're at the VDS index.<BR>" \
    "When you get here, you will have a header with the main project information, " \
    "as well as the complete VDS for the currently selected project (if any).<BR>" \
    "You will also have a button to create a new project and its respective VDS.")

def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "vds/project_details.html", {"project": project})


def document_list(request, project_id):
    """List documents for a project, showing latest revision and key fields.

    The page supports selecting one or more documents and submitting an action
    (delete, replace, issue). For simplicity the view handles a POST with
    action='delete' by deleting the selected documents and redirecting back.
    Other actions are redirected to the first selected document's details
    page (placeholder behavior).
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        selected = request.POST.getlist('selected')
        # normalize to ints
        ids = [int(x) for x in selected if x.isdigit()]
        if action == 'delete' and ids:
            # Delete documents and cascade revisions
            Document.objects.filter(pk__in=ids, project=project).delete()
            return HttpResponseRedirect(reverse('vds:document_list', args=(project_id,)))
        if action in ('replace') and ids:
            # Redirect to first selected document's details as a placeholder
            return HttpResponseRedirect(reverse('vds:document_details', args=(ids[0],)))
        if action in ('issue') and ids:
            transmittal = project.create_transmittal()
            for doc_id in ids:
                # create a new revision for this document with the new transmittal
                Revision.revision_new(transmittal.id, doc_id)
            # Redirect transmittal details
            # load related revisions ordered by document number (smallest first)
            revisions = transmittal.revisions.order_by('document')
            return render(request, "vds/transmittal_details.html", {"transmittal": transmittal, "revisions": revisions})
        # Unknown/no-op -> reload
        return HttpResponseRedirect(reverse('vds:document_list', args=(project_id,)))

    # GET: show documents
    # Use the revision information already stored on the Document object
    # (Document.revision_number). Do not attempt to compute the latest
    # revision from related Revision objects here; if the field is null,
    # that's acceptable and will be displayed as empty.
    documents = list(project.documents.all())


    return render(request, 'vds/document_list.html', {
        'project': project,
        'documents': documents,
    })


def document_details(request, document_id):
    return HttpResponse(f"You're looking at the details of document {document_id}.")


def revision_edit(request, revision_id):
    revision = Revision.objects.get(pk=revision_id)

    return render(request, "vds/revision_edit.html", 
            {
                "revision": revision,
            })


def transmittal_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "vds/transmittal_list.html", {"project": project})

def transmittal_details(request, transmittal_id):
    transmittal = get_object_or_404(Transmittal, pk=transmittal_id)
    # load related revisions ordered by document number (smallest first)
    revisions = transmittal.revisions.order_by('document')
    return render(request, "vds/transmittal_details.html", {"transmittal": transmittal, "revisions": revisions})

def transmittal_new(request, project_id):
    project = Project.objects.get(pk=project_id)
    transmittal = project.create_transmittal()

    return render(request, "vds/transmittal_new.html", 
            {
                "project": project,
                "transmittal": transmittal,
            })

def transmittal_add(request):
    transmittal_id = 1  # placeholder for now
    return HttpResponseRedirect(reverse("vds:transmittal_details", args=(transmittal_id,)))


def transmittal_delete(request, transmittal_id):
    """Delete the transmittal and all related revisions, then redirect.

    This view expects a POST. Permissions and logging are intentionally
    omitted per current scope (to be added later).
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    transmittal = get_object_or_404(Transmittal, pk=transmittal_id)
    project_id = transmittal.project_id
    # cascade delete of revisions will occur because Revision FK uses CASCADE
    transmittal.delete()
    return HttpResponseRedirect(reverse("vds:transmittal_list", args=(project_id,)))

