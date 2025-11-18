#!/usr/bin/env python3
"""
Deidentify ZIP codes in CSV files following HIPAA Safe Harbor guidelines.

This script supports multiple precision levels and fill character options
to accommodate different deidentification requirements.
"""

import csv
import re
import argparse
from pathlib import Path


# Sparsely populated ZIP code prefixes (population < 20,000) based on 2010 Census
SPARSE_ZIP_PREFIXES = {
    '036', '059', '102', '203', '205', '369', '556', '692',
    '821', '823', '878', '879', '884', '893'
}


def deidentify_zipcode(zipcode, precision='smart', fill_char='0', redaction_value='REDACTED_HIPAA'):
    """
    Deidentify a ZIP code according to specified precision and fill character.

    Args:
        zipcode: ZIP code as string or number (5-digit or ZIP+4 format)
        precision: '2', '3', or 'smart' for precision level
        fill_char: '0' or 'X' for fill character
        redaction_value: Value to use when redacting for Safe Harbor compliance

    Returns:
        Deidentified ZIP code string or redaction_value if would violate Safe Harbor
    """
    if not zipcode:
        return zipcode

    # Convert to string and remove any whitespace
    zipcode_str = str(zipcode).strip()

    # Extract digits only (handles ZIP+4 format like '12345-6789')
    digits = re.sub(r'[^\d]', '', zipcode_str)

    # If less than required digits, return as-is
    if len(digits) < 2:
        return zipcode_str

    # Check for Safe Harbor violations in non-smart modes
    if precision in ['2', '3'] and len(digits) >= 3:
        prefix_3digit = digits[:3]
        if prefix_3digit in SPARSE_ZIP_PREFIXES:
            # Using fixed precision on sparse ZIP would violate Safe Harbor
            if precision == '3':
                # 3-digit precision on sparse area reveals too much
                return redaction_value
            elif precision == '2':
                # 2-digit might still be too revealing for very sparse areas
                # For now, allow 2-digit but could be stricter
                pass

    # Determine precision level
    if precision == 'smart':
        # Check if this is a sparsely populated ZIP code prefix
        if len(digits) >= 3 and digits[:3] in SPARSE_ZIP_PREFIXES:
            actual_precision = 2
        else:
            actual_precision = 3
    else:
        actual_precision = int(precision)

    # Ensure we have enough digits
    if len(digits) < actual_precision:
        actual_precision = len(digits)

    # Build deidentified ZIP code
    kept_digits = digits[:actual_precision]
    fill_count = 5 - actual_precision

    return kept_digits + (fill_char * fill_count)


def deidentify_csv(input_file, output_file, zipcode_columns, precision='smart', fill_char='0', delimiter=',', redaction_value='REDACTED_HIPAA'):
    """
    Deidentify ZIP codes in a CSV file.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        zipcode_columns: List of column names or indices containing ZIP codes
        precision: '2', '3', or 'smart' for precision level
        fill_char: '0' or 'X' for fill character
        delimiter: Delimiter character (default: ',')
        redaction_value: Value to use when redacting for Safe Harbor compliance
    """
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter=delimiter)

        if not reader.fieldnames:
            raise ValueError("CSV file appears to be empty or malformed")

        # Determine which columns to deidentify
        # Try to match column names first, then fall back to indices
        columns_to_process = []
        for col in zipcode_columns:
            if isinstance(col, int):
                # Explicit integer type - treat as index
                if 0 <= col < len(reader.fieldnames):
                    columns_to_process.append(reader.fieldnames[col])
                else:
                    print(f"Warning: Column index {col} out of range (max: {len(reader.fieldnames)-1})")
            elif col in reader.fieldnames:
                # String matches a column name - use it
                columns_to_process.append(col)
            elif col.isdigit():
                # String of digits - try as index
                idx = int(col)
                if 0 <= idx < len(reader.fieldnames):
                    columns_to_process.append(reader.fieldnames[idx])
                else:
                    print(f"Warning: Column index {idx} out of range (max: {len(reader.fieldnames)-1})")
            else:
                # String not found in headers
                print(f"Warning: Column '{col}' not found in CSV")

        if not columns_to_process:
            raise ValueError("No valid ZIP code columns found")

        # Stream rows directly to output file to avoid loading all into memory
        row_count = 0
        redaction_count = 0
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, delimiter=delimiter)
            writer.writeheader()

            for row in reader:
                for col in columns_to_process:
                    if col in row:
                        deidentified = deidentify_zipcode(row[col], precision, fill_char, redaction_value)
                        if deidentified == redaction_value:
                            redaction_count += 1
                        row[col] = deidentified
                writer.writerow(row)
                row_count += 1

        print(f"Processed {row_count} rows")
        print(f"Deidentified columns: {', '.join(columns_to_process)}")
        print(f"Precision: {precision}, Fill character: {fill_char}")
        if redaction_count > 0:
            print(f"Warning: {redaction_count} ZIP code(s) replaced with '{redaction_value}' (sparsely populated areas, would violate HIPAA Safe Harbor)")
        print(f"Output saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Deidentify ZIP codes in CSV files following HIPAA Safe Harbor guidelines',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (3-digit precision with zeros)
  %(prog)s input.csv

  # Use X's instead of zeros
  %(prog)s input.csv -f X

  # 2-digit precision
  %(prog)s input.csv -p 2

  # HIPAA-compliant smart mode
  %(prog)s input.csv -p smart -f X

  # Multiple columns
  %(prog)s input.csv -c home_zip work_zip billing_zip

  # Tab-separated file (TSV)
  %(prog)s data.tsv -d $'\\t' -c zipcode

  # Semicolon-separated file
  %(prog)s data.csv -d ';' -c zipcode

  # Pipe-separated file
  %(prog)s data.txt -d '|' -c zipcode
        """
    )
    parser.add_argument(
        'input_file',
        help='Input CSV file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output CSV file path (default: adds _deidentified to input filename)',
        default=None
    )
    parser.add_argument(
        '-c', '--columns',
        nargs='+',
        help='Column names or indices containing ZIP codes (default: "zipcode")',
        default=['zipcode']
    )
    parser.add_argument(
        '-p', '--precision',
        choices=['2', '3', 'smart'],
        default='smart',
        help='Precision level: smart=HIPAA-compliant (default), 3=3-digit, 2=2-digit. Note: Non-smart modes may redact values that violate HIPAA Safe Harbor.'
    )
    parser.add_argument(
        '-f', '--fill',
        choices=['0', 'X'],
        default='0',
        help='Fill character for replaced digits: 0=zeros (default), X=letter X'
    )
    parser.add_argument(
        '-d', '--delimiter',
        default=',',
        help='Delimiter character (default: ","): use "," for CSV, "\\t" for TSV, ";" for semicolon-separated, "|" for pipe-separated'
    )
    parser.add_argument(
        '--redaction-value',
        default='REDACTED_HIPAA',
        help='Value to use when redacting ZIP codes that would violate HIPAA Safe Harbor (default: "REDACTED_HIPAA")'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input_file).exists():
        parser.error(f"Input file not found: {args.input_file}")

    # Set default output filename
    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent / f"{input_path.stem}_deidentified{input_path.suffix}"

    # Handle special delimiter cases (e.g., '\t' for tab)
    # Only decode escape sequences if the string actually contains them
    delimiter = args.delimiter
    if '\\' in delimiter and len(delimiter) > 1:
        try:
            delimiter = delimiter.encode().decode('unicode_escape')
        except (UnicodeDecodeError, ValueError) as e:
            parser.error(f"Invalid delimiter escape sequence '{args.delimiter}': {e}")

    # Validate delimiter is a single character
    if len(delimiter) != 1:
        parser.error(f"Delimiter must be a single character, got: '{delimiter}' (length {len(delimiter)})")

    # Process the CSV file
    # Pass column arguments as-is; deidentify_csv will handle name vs. index resolution
    try:
        deidentify_csv(args.input_file, args.output, args.columns, args.precision, args.fill, delimiter, args.redaction_value)
    except Exception as e:
        parser.error(f"Error processing CSV: {e}")


if __name__ == '__main__':
    main()
