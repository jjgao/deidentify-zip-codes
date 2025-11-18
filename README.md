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
# Default mode (3-digit precision with zeros)
python3 deidentify_zipcode.py input.csv
```

This will create `input_deidentified.csv` with ZIP codes converted from `12345` → `12300`.

### Precision Options

```bash
# 2-digit precision
python3 deidentify_zipcode.py input.csv -p 2
# Result: 12345 → 12000

# 3-digit precision (default)
python3 deidentify_zipcode.py input.csv -p 3
# Result: 12345 → 12300

# Smart mode (HIPAA-compliant)
python3 deidentify_zipcode.py input.csv -p smart
# Result: 12345 → 12300, but 03601 → 03000 (sparse area)
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

### Complete Example

```bash
# HIPAA-compliant with X's, multiple columns, custom output
python3 deidentify_zipcode.py patients.csv \
  -c home_zipcode work_zipcode \
  -p smart \
  -f X \
  -o patients_deidentified.csv
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
                             [-p {2,3,smart}] [-f {0,X}]
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
                        Precision level: 2=2-digit, 3=3-digit (default), smart=HIPAA-compliant
  -f {0,X}, --fill {0,X}
                        Fill character for replaced digits: 0=zeros (default), X=letter X
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

- **5-digit ZIP codes**: `12345`
- **ZIP+4 format**: `12345-6789` (hyphen and extension removed)
- **Leading zeros**: `00501` (preserved)
- **Empty values**: Preserved as-is

## Requirements

- Python 3.6 or later
- No external dependencies (uses only standard library)

## License

This project is released under the MIT License.

## Contributing

Contributions are welcome! Please see REQUIREMENTS.md for detailed specifications.

## References

- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html)
- [HIPAA Safe Harbor De-identification](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)