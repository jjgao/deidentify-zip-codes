#!/usr/bin/env python3
"""
Unit tests for deidentify_zipcode.py

Run with: python3 test_deidentify_zipcode.py
"""

import unittest
import csv
import os
from pathlib import Path
from deidentify_zipcode import deidentify_zipcode, deidentify_csv, SPARSE_ZIP_PREFIXES


class TestDeidentifyZipcode(unittest.TestCase):
    """Test cases for ZIP code deidentification functions"""

    def test_3digit_zeros_normal(self):
        """Test 3-digit precision with zeros for normal ZIP codes"""
        self.assertEqual(deidentify_zipcode('12345', '3', '0'), '12300')
        self.assertEqual(deidentify_zipcode('90210', '3', '0'), '90200')
        self.assertEqual(deidentify_zipcode('00501', '3', '0'), '00500')

    def test_3digit_x_normal(self):
        """Test 3-digit precision with X's for normal ZIP codes"""
        self.assertEqual(deidentify_zipcode('12345', '3', 'X'), '123XX')
        self.assertEqual(deidentify_zipcode('90210', '3', 'X'), '902XX')
        self.assertEqual(deidentify_zipcode('00501', '3', 'X'), '005XX')

    def test_2digit_zeros(self):
        """Test 2-digit precision with zeros"""
        self.assertEqual(deidentify_zipcode('12345', '2', '0'), '12000')
        self.assertEqual(deidentify_zipcode('90210', '2', '0'), '90000')
        self.assertEqual(deidentify_zipcode('00501', '2', '0'), '00000')

    def test_2digit_x(self):
        """Test 2-digit precision with X's"""
        self.assertEqual(deidentify_zipcode('12345', '2', 'X'), '12XXX')
        self.assertEqual(deidentify_zipcode('90210', '2', 'X'), '90XXX')
        self.assertEqual(deidentify_zipcode('00501', '2', 'X'), '00XXX')

    def test_smart_mode_normal_zeros(self):
        """Test smart mode with zeros for normal population ZIP codes"""
        self.assertEqual(deidentify_zipcode('12345', 'smart', '0'), '12300')
        self.assertEqual(deidentify_zipcode('90210', 'smart', '0'), '90200')
        self.assertEqual(deidentify_zipcode('94102', 'smart', '0'), '94100')

    def test_smart_mode_normal_x(self):
        """Test smart mode with X's for normal population ZIP codes"""
        self.assertEqual(deidentify_zipcode('12345', 'smart', 'X'), '123XX')
        self.assertEqual(deidentify_zipcode('90210', 'smart', 'X'), '902XX')
        self.assertEqual(deidentify_zipcode('94102', 'smart', 'X'), '941XX')

    def test_smart_mode_sparse_zeros(self):
        """Test smart mode with zeros for sparsely populated ZIP codes"""
        # Test all sparse prefixes
        self.assertEqual(deidentify_zipcode('03601', 'smart', '0'), '03000')  # 036
        self.assertEqual(deidentify_zipcode('05901', 'smart', '0'), '05000')  # 059
        self.assertEqual(deidentify_zipcode('10234', 'smart', '0'), '10000')  # 102
        self.assertEqual(deidentify_zipcode('20301', 'smart', '0'), '20000')  # 203
        self.assertEqual(deidentify_zipcode('20501', 'smart', '0'), '20000')  # 205
        self.assertEqual(deidentify_zipcode('36901', 'smart', '0'), '36000')  # 369
        self.assertEqual(deidentify_zipcode('55601', 'smart', '0'), '55000')  # 556
        self.assertEqual(deidentify_zipcode('69201', 'smart', '0'), '69000')  # 692
        self.assertEqual(deidentify_zipcode('82101', 'smart', '0'), '82000')  # 821
        self.assertEqual(deidentify_zipcode('82301', 'smart', '0'), '82000')  # 823
        self.assertEqual(deidentify_zipcode('87801', 'smart', '0'), '87000')  # 878
        self.assertEqual(deidentify_zipcode('87901', 'smart', '0'), '87000')  # 879
        self.assertEqual(deidentify_zipcode('88401', 'smart', '0'), '88000')  # 884
        self.assertEqual(deidentify_zipcode('89301', 'smart', '0'), '89000')  # 893

    def test_smart_mode_sparse_x(self):
        """Test smart mode with X's for sparsely populated ZIP codes"""
        self.assertEqual(deidentify_zipcode('03601', 'smart', 'X'), '03XXX')  # 036
        self.assertEqual(deidentify_zipcode('05901', 'smart', 'X'), '05XXX')  # 059
        self.assertEqual(deidentify_zipcode('10234', 'smart', 'X'), '10XXX')  # 102
        self.assertEqual(deidentify_zipcode('82101', 'smart', 'X'), '82XXX')  # 821
        self.assertEqual(deidentify_zipcode('89301', 'smart', 'X'), '89XXX')  # 893

    def test_zip_plus_4_format(self):
        """Test ZIP+4 format handling"""
        self.assertEqual(deidentify_zipcode('12345-6789', '3', '0'), '12300')
        self.assertEqual(deidentify_zipcode('12345-6789', '3', 'X'), '123XX')
        self.assertEqual(deidentify_zipcode('12345-6789', '2', '0'), '12000')
        self.assertEqual(deidentify_zipcode('03601-1234', 'smart', '0'), '03000')
        self.assertEqual(deidentify_zipcode('03601-1234', 'smart', 'X'), '03XXX')

    def test_empty_values(self):
        """Test handling of empty/null values"""
        self.assertEqual(deidentify_zipcode('', '3', '0'), '')
        self.assertEqual(deidentify_zipcode(None, '3', '0'), None)
        # Whitespace-only strings are stripped to empty
        self.assertEqual(deidentify_zipcode('   ', '3', '0'), '')

    def test_short_zipcodes(self):
        """Test handling of ZIP codes with less than required digits"""
        # Less than 2 digits - should return as-is
        self.assertEqual(deidentify_zipcode('1', '3', '0'), '1')
        self.assertEqual(deidentify_zipcode('', '3', '0'), '')

        # Exactly 2 digits with 2-digit precision
        self.assertEqual(deidentify_zipcode('12', '2', '0'), '12000')

        # 2 digits with 3-digit precision (fallback to 2-digit)
        self.assertEqual(deidentify_zipcode('12', '3', '0'), '12000')

    def test_numeric_input(self):
        """Test handling of numeric ZIP codes (not strings)"""
        self.assertEqual(deidentify_zipcode(12345, '3', '0'), '12300')
        self.assertEqual(deidentify_zipcode(501, '3', '0'), '50100')
        self.assertEqual(deidentify_zipcode(12345, 'smart', 'X'), '123XX')

    def test_whitespace_handling(self):
        """Test handling of ZIP codes with whitespace"""
        self.assertEqual(deidentify_zipcode(' 12345 ', '3', '0'), '12300')
        self.assertEqual(deidentify_zipcode('12345 ', '3', 'X'), '123XX')

    def test_all_sparse_prefixes_defined(self):
        """Verify all sparse prefixes are correctly defined"""
        expected_sparse = {'036', '059', '102', '203', '205', '369',
                          '556', '692', '821', '823', '878', '879',
                          '884', '893'}
        self.assertEqual(SPARSE_ZIP_PREFIXES, expected_sparse)


class TestDeidentifyCSV(unittest.TestCase):
    """Test cases for CSV file processing"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path('test_data')
        self.test_dir.mkdir(exist_ok=True)

        # Create test CSV
        self.test_input = self.test_dir / 'test_input.csv'
        self.test_output = self.test_dir / 'test_output.csv'

        with open(self.test_input, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'zipcode', 'work_zip'])
            writer.writerow(['1', 'Alice', '12345', '90210'])
            writer.writerow(['2', 'Bob', '03601', '82101'])
            writer.writerow(['3', 'Charlie', '94102-5678', '00501'])

    def tearDown(self):
        """Clean up test files"""
        if self.test_input.exists():
            self.test_input.unlink()
        if self.test_output.exists():
            self.test_output.unlink()
        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_csv_single_column_default(self):
        """Test CSV processing with single column and default settings"""
        deidentify_csv(self.test_input, self.test_output, ['zipcode'])

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(rows[0]['zipcode'], '12300')
        self.assertEqual(rows[1]['zipcode'], '03600')
        self.assertEqual(rows[2]['zipcode'], '94100')

        # Work_zip should be unchanged
        self.assertEqual(rows[0]['work_zip'], '90210')

    def test_csv_multiple_columns(self):
        """Test CSV processing with multiple columns"""
        deidentify_csv(self.test_input, self.test_output,
                      ['zipcode', 'work_zip'], '3', 'X')

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(rows[0]['zipcode'], '123XX')
        self.assertEqual(rows[0]['work_zip'], '902XX')
        self.assertEqual(rows[1]['zipcode'], '036XX')
        self.assertEqual(rows[1]['work_zip'], '821XX')

    def test_csv_smart_mode(self):
        """Test CSV processing with smart mode"""
        deidentify_csv(self.test_input, self.test_output,
                      ['zipcode', 'work_zip'], 'smart', '0')

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Normal population ZIP
        self.assertEqual(rows[0]['zipcode'], '12300')
        self.assertEqual(rows[0]['work_zip'], '90200')

        # Sparse population ZIPs
        self.assertEqual(rows[1]['zipcode'], '03000')
        self.assertEqual(rows[1]['work_zip'], '82000')

        # Normal population ZIP with ZIP+4
        self.assertEqual(rows[2]['zipcode'], '94100')

    def test_csv_column_by_index(self):
        """Test CSV processing using column indices"""
        deidentify_csv(self.test_input, self.test_output, [2, 3], '2', '0')

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(rows[0]['zipcode'], '12000')
        self.assertEqual(rows[0]['work_zip'], '90000')

    def test_csv_preserves_other_columns(self):
        """Test that CSV processing preserves non-ZIP columns"""
        deidentify_csv(self.test_input, self.test_output, ['zipcode'])

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Check other columns are unchanged
        self.assertEqual(rows[0]['id'], '1')
        self.assertEqual(rows[0]['name'], 'Alice')
        self.assertEqual(rows[1]['id'], '2')
        self.assertEqual(rows[1]['name'], 'Bob')

    def test_csv_preserves_structure(self):
        """Test that CSV structure (headers, row count) is preserved"""
        deidentify_csv(self.test_input, self.test_output, ['zipcode'])

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 3)
        self.assertEqual(list(rows[0].keys()), ['id', 'name', 'zipcode', 'work_zip'])

    def test_csv_digit_column_name(self):
        """Test CSV with digit-only column names (e.g., year columns like '2023')"""
        # Create test file with digit column names
        test_file = self.test_dir / 'test_digit_columns.csv'
        test_out = self.test_dir / 'test_digit_out.csv'

        with open(test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', '2023', '2024'])
            writer.writerow(['1', '12345', '90210'])
            writer.writerow(['2', '03601', '82101'])

        # Test selecting digit column by name (should work now)
        deidentify_csv(test_file, test_out, ['2023', '2024'], '3', '0')

        with open(test_out, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(rows[0]['2023'], '12300')
        self.assertEqual(rows[0]['2024'], '90200')
        self.assertEqual(rows[1]['2023'], '03600')
        self.assertEqual(rows[1]['2024'], '82100')

        # Clean up
        test_file.unlink()
        test_out.unlink()

    def test_csv_string_index_vs_name(self):
        """Test that string indices ('0', '1') work as indices when no matching column name"""
        # Using existing test file where column 2 is 'zipcode', column 3 is 'work_zip'
        deidentify_csv(self.test_input, self.test_output, ['2', '3'], '3', 'X')

        with open(self.test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Columns at index 2 and 3 should be deidentified
        self.assertEqual(rows[0]['zipcode'], '123XX')
        self.assertEqual(rows[0]['work_zip'], '902XX')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_leading_zeros_preserved(self):
        """Test that leading zeros are preserved in output"""
        self.assertEqual(deidentify_zipcode('00501', '3', '0'), '00500')
        self.assertEqual(deidentify_zipcode('00501', '3', 'X'), '005XX')
        self.assertEqual(deidentify_zipcode('00501', '2', '0'), '00000')

    def test_special_sparse_cases(self):
        """Test edge cases for sparse ZIP detection"""
        # 102 is sparse
        self.assertEqual(deidentify_zipcode('10234', 'smart', '0'), '10000')

        # 101 is NOT sparse (should use 3-digit)
        self.assertEqual(deidentify_zipcode('10134', 'smart', '0'), '10100')

        # 036 is sparse
        self.assertEqual(deidentify_zipcode('03601', 'smart', '0'), '03000')

        # 037 is NOT sparse (should use 3-digit)
        self.assertEqual(deidentify_zipcode('03701', 'smart', '0'), '03700')

    def test_boundary_cases(self):
        """Test boundary cases for ZIP codes"""
        # Minimum valid 5-digit ZIP
        self.assertEqual(deidentify_zipcode('00001', '3', '0'), '00000')

        # Maximum valid 5-digit ZIP
        self.assertEqual(deidentify_zipcode('99950', '3', '0'), '99900')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDeidentifyZipcode))
    suite.addTests(loader.loadTestsFromTestCase(TestDeidentifyCSV))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
