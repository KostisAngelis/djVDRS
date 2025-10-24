import unittest

from vds.models import Document
from vds.utils import _increment_numeric, _increment_alpha


class DummyDocument:
    def __init__(self, revision_number=None):
        self.revision_number = revision_number


class TestRevisionLabelSimple(unittest.TestCase):
    def test_numeric_helper(self):
        self.assertEqual(_increment_numeric('2'), '3')
        self.assertEqual(_increment_numeric('009'), '010')

    def test_alpha_helper(self):
        self.assertEqual(_increment_alpha('a'), 'b')
        self.assertEqual(_increment_alpha('A'), 'B')
        self.assertEqual(_increment_alpha('Z'), 'Z')

    def test_document_increment_with_revision_set(self):
        d = DummyDocument(revision_number='01')
        # call the Document method using the dummy instance as self
        result = Document.revision_next(d)
        self.assertEqual(result, '02')

    def test_document_no_revision_returns_empty(self):
        d = DummyDocument(revision_number=None)
        result = Document.revision_next(d)
        # when no revision_number is set, the method now returns '0'
        self.assertEqual(result, '0')


if __name__ == '__main__':
    unittest.main()

