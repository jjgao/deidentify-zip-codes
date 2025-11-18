# ZIP Code Deidentification Tool

A Python script to deidentify ZIP codes in CSV files following HIPAA Safe Harbor guidelines.

## Features

- **Multiple Precision Levels**: Choose between 2-digit, 3-digit, or smart (HIPAA-compliant) precision
- **Flexible Fill Characters**: Use zeros (0) or X's for replaced digits
- **HIPAA Safe Harbor Compliance**: Smart mode automatically handles sparsely populated ZIP codes
- **Multi-Column Support**: Process multiple ZIP code columns in a single pass
- **ZIP+4 Support**: Handles both 5-digit and ZIP+4 format codes

## Installation

No installation required! This script uses only Python standard library. Just ensure you have Python 3.6 or later:

```bash
python3 --version
```

## Usage

### Basic Usage

```bash
# Default mode (smart/HIPAA-compliant precision with zeros)
# If your CSV has a column named 'zipcode':
python3 deidentify_zipcode.py input.csv

# If your columns have different names, specify them:
python3 deidentify_zipcode.py input.csv -c home_zipcode work_zipcode
```

This will create `input_deidentified.csv` with ZIP codes converted from `12345` → `12300` (3-digit for normal populations) and `03601` → `03000` (2-digit for sparse populations).

### Precision Options

```bash
# 2-digit precision
python3 deidentify_zipcode.py input.csv -p 2
# Result: 12345 → 12000, 03601 → 03000

# 3-digit precision (may redact sparse areas)
python3 deidentify_zipcode.py input.csv -p 3
# Result: 12345 → 12300
# Note: Sparse ZIPs like 03601 will be replaced with 'REDACTED_HIPAA' to avoid HIPAA violations

# Smart mode (HIPAA-compliant, default - never redacts)
python3 deidentify_zipcode.py input.csv -p smart
# Result: 12345 → 12300, but 03601 → 03000 (sparse area automatically gets 2-digit)
# Smart mode adjusts precision instead of redacting, so no data loss
```

### Fill Character Options

```bash
# Use X's instead of zeros
python3 deidentify_zipcode.py input.csv -f X
# Result: 12345 → 123XX

# Combine with 2-digit precision
python3 deidentify_zipcode.py input.csv -p 2 -f X
# Result: 12345 → 12XXX
```

### Column Selection

```bash
# Specify column by name
python3 deidentify_zipcode.py input.csv -c zipcode

# Multiple columns
python3 deidentify_zipcode.py input.csv -c home_zip work_zip billing_zip

# Use column index (0-based)
python3 deidentify_zipcode.py input.csv -c 0 3
```

### Custom Output File

```bash
python3 deidentify_zipcode.py input.csv -o output.csv
```

### Delimiter Options

```bash
# Tab-separated file (TSV)
python3 deidentify_zipcode.py data.tsv -d $'\t' -c zipcode

# Semicolon-separated file (common in European locales)
python3 deidentify_zipcode.py data.csv -d ';' -c zipcode

# Pipe-separated file (common in data warehousing)
python3 deidentify_zipcode.py data.txt -d '|' -c zipcode

# Custom delimiter
python3 deidentify_zipcode.py data.txt -d ':' -c zipcode
```

### Redaction Value

When using `-p 3` (fixed 3-digit precision) on sparsely populated ZIP codes, the tool will redact values to prevent HIPAA Safe Harbor violations:

```bash
# Default redaction value
python3 deidentify_zipcode.py input.csv -p 3
# Sparse ZIP 03601 becomes: REDACTED_HIPAA

# Custom redaction value
python3 deidentify_zipcode.py input.csv -p 3 --redaction-value "[REMOVED]"
# Sparse ZIP 03601 becomes: [REMOVED]

# Smart mode never redacts (adjusts precision instead)
python3 deidentify_zipcode.py input.csv -p smart
# Sparse ZIP 03601 becomes: 03000
```

### Complete Example

```bash
# HIPAA-compliant with X's, multiple columns, custom output
python3 deidentify_zipcode.py patients.csv \
  -c home_zipcode work_zipcode \
  -p smart \
  -f X \
  -o patients_deidentified.csv

# Tab-separated file with smart mode
python3 deidentify_zipcode.py patients.tsv \
  -d $'\t' \
  -c zipcode \
  -p smart \
  -f 0
```

## HIPAA Safe Harbor Compliance

### What is Smart Mode?

The HIPAA Safe Harbor method requires special handling for sparsely populated areas. According to HIPAA guidelines:

- ZIP codes with 3-digit prefixes representing populations **≥ 20,000**: Keep 3 digits
- ZIP codes with 3-digit prefixes representing populations **< 20,000**: Keep only 2 digits

### Sparsely Populated ZIP Code Prefixes

Based on 2010 Census data, the following 3-digit prefixes are considered sparsely populated:

```
036, 059, 102, 203, 205, 369, 556, 692, 821, 823, 878, 879, 884, 893
```

### Smart Mode Examples

| Original | Smart Mode (zeros) | Smart Mode (X's) | Reason |
|----------|-------------------|------------------|---------|
| 12345 | 12300 | 123XX | Normal population |
| 90210 | 90200 | 902XX | Normal population |
| 03601 | 03000 | 03XXX | Sparse (prefix 036) |
| 82101 | 82000 | 82XXX | Sparse (prefix 821) |
| 89301 | 89000 | 89XXX | Sparse (prefix 893) |

## Examples

See `example_input.csv` for sample data. Try these commands:

```bash
# Test default mode
python3 deidentify_zipcode.py example_input.csv -c home_zipcode work_zipcode

# Test smart mode with X's
python3 deidentify_zipcode.py example_input.csv -c home_zipcode work_zipcode -p smart -f X

# Test 2-digit mode
python3 deidentify_zipcode.py example_input.csv -c home_zipcode work_zipcode -p 2
```

## Command-Line Options

```
usage: deidentify_zipcode.py [-h] [-o OUTPUT] [-c COLUMNS [COLUMNS ...]]
                             [-p {2,3,smart}] [-f {0,X}] [-d DELIMITER]
                             [--redaction-value REDACTION_VALUE]
                             input_file

positional arguments:
  input_file            Input CSV file path

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output CSV file path (default: adds _deidentified to input filename)
  -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                        Column names or indices containing ZIP codes (default: "zipcode")
  -p {2,3,smart}, --precision {2,3,smart}
                        Precision level: smart=HIPAA-compliant (default), 3=3-digit, 2=2-digit.
                        Note: Non-smart modes may redact values that violate HIPAA Safe Harbor.
  -f {0,X}, --fill {0,X}
                        Fill character for replaced digits: 0=zeros (default), X=letter X
  -d DELIMITER, --delimiter DELIMITER
                        Delimiter character (default: ","): use "," for CSV, "\t" for TSV,
                        ";" for semicolon-separated, "|" for pipe-separated
  --redaction-value REDACTION_VALUE
                        Value to use when redacting ZIP codes that would violate HIPAA Safe Harbor
                        (default: "REDACTED_HIPAA")
```

## How It Works

1. **Reads CSV file**: Preserves all columns and data structure
2. **Identifies ZIP code columns**: By name or index
3. **Deidentifies ZIP codes**:
   - Extracts digits from ZIP code (handles ZIP+4 format)
   - Determines precision level (2, 3, or smart)
   - Replaces trailing digits with fill character
4. **Writes output**: Creates new CSV file with deidentified data

## Supported Input Formats

### ZIP Code Formats
- **5-digit ZIP codes**: `12345`
- **ZIP+4 format**: `12345-6789` (hyphen and extension removed)
- **Leading zeros**: `00501` (preserved)
- **Empty values**: Preserved as-is

### File Formats
- **CSV** (comma-separated): Default delimiter `,`
- **TSV** (tab-separated): Use `-d $'\t'`
- **Semicolon-separated**: Use `-d ';'` (common in European locales)
- **Pipe-separated**: Use `-d '|'` (common in data warehousing)
- **Custom delimiters**: Any single character

## Requirements

- Python 3.6 or later
- No external dependencies (uses only standard library)

## Testing

The project includes comprehensive unit tests covering all functionality.

### Run Tests

```bash
python3 test_deidentify_zipcode.py
```

### Test Coverage

The test suite includes 38 tests covering:
- All precision modes (2-digit, 3-digit, smart)
- Both fill characters (zeros and X's)
- All 14 sparsely populated ZIP code prefixes
- ZIP+4 format handling
- **Delimiter support** (comma, tab, semicolon, pipe)
- **Redaction behavior** for HIPAA Safe Harbor violations:
  - `-p 3` redacts sparse ZIP codes
  - Smart mode never redacts (adjusts precision instead)
  - Malformed/truncated ZIP codes with 2 digits (only with `-p 3`)
- Custom redaction values
- Edge cases (empty values, leading zeros, whitespace)
- CSV file processing with single and multiple columns
- Data integrity and structure preservation
- Digit-only column names
- Isolated test environments using temporary directories

All tests pass successfully.

## License

This project is released under the MIT License.

## Contributing

Contributions are welcome! Please see REQUIREMENTS.md for detailed specifications.

## References

- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html)
- [HIPAA Safe Harbor De-identification](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)