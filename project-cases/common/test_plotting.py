"""Evidence validation must prevent misleading graphs."""
import csv
import tempfile
import unittest
from pathlib import Path
from plotting import number, read_rows, unique, constant

class EvidenceTests(unittest.TestCase):
    def test_reject_nonfinite_or_negative_measurement(self):
        for value in ['nan', 'inf', '-1']:
            with self.assertRaises(ValueError): number({'ms':value}, 'ms')
    def test_duplicate_session_rejected(self):
        with self.assertRaises(ValueError): unique([{'clients':'1'},{'clients':'1'}], ['clients'])
    def test_changed_controls_rejected(self):
        with self.assertRaises(ValueError): constant([{'seed':'1'},{'seed':'2'}], ['seed'])
    def test_failed_correctness_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'result.csv'
            path.write_text('correct,ms\nFAIL,1\n')
            with self.assertRaises(ValueError): read_rows(path)
    def test_valid_zero_error_count(self):
        self.assertEqual(number({'error_count':'0'}, 'error_count'),0)

if __name__=='__main__': unittest.main()
