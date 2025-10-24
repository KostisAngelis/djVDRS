from django.db import models
from django.db.models import Q, UniqueConstraint
from django.core.exceptions import ValidationError
import re
import datetime

from vds.utils import _increment_numeric, _increment_alpha


class Project(models.Model):
    wa_number = models.CharField("WA number", max_length=20, unique=True)
    client_number = models.CharField("Client project number", max_length=50)
    drm_ref_number = models.CharField("DrM project reference number", max_length=20)
    title = models.CharField("Project Title", max_length=100)
    stub = models.CharField("Project Stub", max_length=10)
    client_title = models.CharField("Client title", max_length=100)
    country = models.CharField("Country", max_length=200)
    location = models.CharField("Location", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.wa_number} - {self.title}"

    def create_transmittal(self, source: str | None = None):
        """Create and return a new Transmittal for this Project.

        - `source`: optional source string. If None, the source of the
          first (earliest) existing transmittal for this project is used.
          If there are no existing transmittals and no source provided,
          the source defaults to the string 'HOUSE'.
        - The new transmittal's `number` is computed by taking the most
          recent transmittal for this project with the chosen source and
          incrementing any trailing digits (preserving zero-padding). If
          no matching transmittal exists, numbering starts at '001'. If the
          most recent number has no trailing digits, '001' is appended.

        Returns the created Transmittal instance (saved to the database).
        """

        # determine source if not provided
        if source is None:
            first = self.transmittals.order_by('date_sent', 'id').first()
            if first is not None:
                source = first.source
            else:
                source = 'HOUSE'

        # find the most recent transmittal with this source
        latest = self.transmittals.filter(source=source).order_by('-date_sent', '-id').first()
        if latest is not None:
            num = latest.number or ''
            # find the last numeric group and any trailing non-digit suffix
            m = re.search(r'^(.*?)(\d+)(\D*)$', num)
            if m:
                prefix, digits, suffix = m.group(1), m.group(2), m.group(3)
                new_digits = _increment_numeric(digits)
                new_number = f"{prefix}{new_digits}{suffix}"
            else:
                # no numeric group -> append '-001'
                new_number = f"{num}-001" if num else 'TR-001'
        else:
            new_number = 'TR-001'

        # create and return the new Transmittal; date_sent set to today
        today = datetime.date.today()
        return self.transmittals.create(number=new_number, source=source, date_sent=today)


class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField("Document Title", max_length=255)
    vds_status = models.CharField("VDS status", max_length=15,default="Active")
    stub = models.CharField("Stub", max_length=100)
    discipline = models.CharField("Discipline", max_length=100)
    document_number = models.CharField("Document number", max_length=100, unique=True, db_index=True)
    client_number = models.CharField("Client number", max_length=255, null=True, blank=True)
    supplier_number = models.CharField("Supplier number", max_length=255, null=True, blank=True)
    revision_number = models.CharField("Revision number", max_length=10, null=True, blank=True)
    required_by = models.DateField("Required by", null=True, blank=True)
    first_issue = models.DateField("First issue", null=True, blank=True)
    latest_issue = models.DateField("Latest issue", null=True, blank=True)
    next_due = models.DateField("Next due", null=True, blank=True)
    notes = models.CharField("Notes", max_length=255, blank=True, default='')
    penalty = models.BooleanField("Penalty", default=False)
    milestone = models.BooleanField("Milestone", default=False)
    priority = models.BooleanField("Priority", default=False)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        constraints = [
            # enforce uniqueness only when client_number is not null
            UniqueConstraint(fields=['client_number'], condition=~Q(client_number=None), name='unique_client_number_not_null'),
            # enforce uniqueness only when supplier_number is not null
            UniqueConstraint(fields=['supplier_number'], condition=~Q(supplier_number=None), name='unique_supplier_number_not_null'),
        ]

    def __str__(self):
        return f"{self.document_number} - {self.title}"

    def revision_next(self) -> str:
        """Return the next revision label for this Document.

        Uses the document's `revision_number` field if present, otherwise
        does nothing if the document has no `revision_number` set. Behavior
        and rules are the same as the module-level helpers: numeric preserves
        zero-padding, alphabetic uses per-character increment with Z/z
        preserved.
        """
        s = getattr(self, 'revision_number', None)
        if not s:
            # Return '0' as the default starting label when missing.
            return '0'

        m = re.match(r'^([0-9]+|[A-Za-z]+)', s)
        if not m:
            return s

        rev = m.group(1)
        if rev.isdigit():
            return _increment_numeric(rev)
        return _increment_alpha(rev)


class Transmittal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transmittals')
    number = models.CharField("Number", max_length=50, unique=True)
    source = models.CharField("Source", max_length=30)
    date_sent = models.DateField("Date sent")
    notes = models.CharField("Notes", max_length=100, blank=True, default='')

    class Meta:
        verbose_name = "Transmittal"
        verbose_name_plural = "Transmittals"

    def __str__(self):
        return f"Transmittal {self.number} (sent: {self.date_sent})"


class Revision(models.Model):
    transmittal = models.ForeignKey(Transmittal, on_delete=models.CASCADE,
                                 related_name='revisions')
    document = models.ForeignKey(Document, on_delete=models.CASCADE,
                              related_name='revisions')
    revision_number = models.CharField("Revision number", max_length=10)
    date = models.DateField("Date")
    purpose = models.CharField("Purpose", max_length=50)
    prepared_by = models.CharField("Prepared by", max_length=10, null=True, blank=True)
    reviewed_by = models.CharField("Reviewed by", max_length=10, null=True, blank=True)
    approved_by = models.CharField("Approved by", max_length=10, null=True, blank=True)
    notes = models.CharField("Notes", max_length=50, blank=True, default='')

    class Meta:
        verbose_name = "Revision"
        verbose_name_plural = "Revisions"
        ordering = ['-date']
        constraints = [
            UniqueConstraint(fields=['document', 'revision_number'], name='unique_revision_per_document'),
            UniqueConstraint(fields=['transmittal','document', ], name='unique_document_per_transmittal')
        ]

    def __str__(self):
        return f"{self.document.document_number} rev {self.revision_number}"
    

    @classmethod
    def revision_new(cls, transmittal_id: int, document_id: int):
        """Create a new Revision for the given transmittal and document IDs.

        - Uses Document.revision_next() to obtain the next revision label.
        - Sets date to today, purpose to 'IFR - Issued for Review', notes empty.
        - Copies prepared_by/reviewed_by/approved_by from the latest existing
          revision for the same document when present; otherwise uses '*'.
        - Updates the Document.revision_number and latest_issue to reflect the
          newly created revision.

        Returns the created Revision instance.
        """
        # Fetch related objects (let exceptions bubble as appropriate)
        transmittal = Transmittal.objects.get(pk=transmittal_id)
        document = Document.objects.get(pk=document_id)

        # Determine new revision label from Document helper
        new_label = document.revision_next()

        today = datetime.date.today()

        # Find latest existing revision for this document, if any
        latest = cls.objects.filter(document=document).order_by('-date').first()

        prepared_by = getattr(latest, 'prepared_by', None)
        reviewed_by = getattr(latest, 'reviewed_by', None)
        approved_by = getattr(latest, 'approved_by', None)

        # Create the new revision
        new_rev = cls.objects.create(
            transmittal=transmittal,
            document=document,
            revision_number=new_label,
            date=today,
            purpose='IFR - Issued for Review',
            prepared_by=prepared_by,
            reviewed_by=reviewed_by,
            approved_by=approved_by,
            notes=''
        )

        # Update the Document to reflect the new latest revision and issue date
        document.revision_number = new_label
        document.latest_issue = today
        document.save(update_fields=['revision_number', 'latest_issue'])

        return new_rev


