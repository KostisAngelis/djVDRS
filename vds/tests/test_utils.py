import unittest

from vds.utils import _increment_numeric, _increment_alpha


class TestUtils(unittest.TestCase):
    def test_increment_numeric_basic(self):
        self.assertEqual(_increment_numeric('0'), '1')
        self.assertEqual(_increment_numeric('9'), '10')
        self.assertEqual(_increment_numeric('099'), '100')

    def test_increment_numeric_invalid(self):
        self.assertEqual(_increment_numeric('a1'), 'a1')

    def test_increment_alpha_basic(self):
        self.assertEqual(_increment_alpha('a'), 'b')
        self.assertEqual(_increment_alpha('A'), 'B')

    def test_increment_alpha_z_preserved(self):
        self.assertEqual(_increment_alpha('Z'), 'Z')
        self.assertEqual(_increment_alpha('z'), 'z')


if __name__ == '__main__':
    unittest.main()
