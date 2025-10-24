from django.test import TestCase
import datetime

from vds.models import Project, Transmittal


class ProjectCreateTransmittalTests(TestCase):
    def _create_project(self):
        return Project.objects.create(
            wa_number='WA-X', client_number='C-X', drm_ref_number='DRMX',
            title='P X', stub='PX', client_title='PXT', country='Nowhere'
        )

    def test_create_first_transmittal_defaults(self):
        p = self._create_project()
        t = p.create_transmittal(source=None)
        self.assertIsInstance(t, Transmittal)
        self.assertEqual(t.number, 'TR-001')
        self.assertEqual(t.source, 'HOUSE')

    def test_increment_trailing_digits_preserves_padding(self):
        p = self._create_project()
        p.transmittals.create(number='T009', source='S1', date_sent=datetime.date(2025, 1, 1))
        t2 = p.create_transmittal(source='S1')
        self.assertEqual(t2.number, 'T010')

    def test_append_one_when_no_digits(self):
        p = self._create_project()
        p.transmittals.create(number='ABC', source='S2', date_sent=datetime.date(2025, 1, 2))
        t2 = p.create_transmittal(source='S2')
        # when no numeric group exists, we append '-001'
        self.assertEqual(t2.number, 'ABC-001')

    def test_use_first_transmittal_source_when_none(self):
        p = self._create_project()
        # earliest transmittal has source 'EARLY'
        p.transmittals.create(number='X1', source='EARLY', date_sent=datetime.date(2024, 1, 1))
        p.transmittals.create(number='Y1', source='LATE', date_sent=datetime.date(2024, 6, 1))
        t = p.create_transmittal(None)
        self.assertEqual(t.source, 'EARLY')
        # since no existing EARLY with trailing digits, number should be 'X11'??
        # In our implementation, latest for source EARLY is X1 -> no trailing digits -> append '1'
        self.assertEqual(t.number, 'X2')

    def test_most_recent_matching_source_selected(self):
        p = self._create_project()
        # older matching
        p.transmittals.create(number='S3001', source='S3', date_sent=datetime.date(2024, 1, 1))
        # newer matching with digits
        p.transmittals.create(number='S3009', source='S3', date_sent=datetime.date(2025, 1, 1))
        t = p.create_transmittal('S3')
        self.assertEqual(t.number, 'S3010')

    def test_preserve_non_numeric_suffix(self):
        p = self._create_project()
        # number ends with digits followed by a letter suffix
        p.transmittals.create(number='DOC-009A', source='S4', date_sent=datetime.date(2025, 1, 1))
        t = p.create_transmittal('S4')
        # numeric part 009 -> 010, suffix 'A' preserved
        self.assertEqual(t.number, 'DOC-010A')

    def test_custom_source_not_existing_starts_at_one(self):
        p = self._create_project()
        t = p.create_transmittal('BrandNew')
        self.assertEqual(t.source, 'BrandNew')
        # new numbering starts at TR-001 per new policy
        self.assertEqual(t.number, 'TR-001')
