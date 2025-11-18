# ZIP Code Deidentification Script - Requirements

## Overview
A Python script to deidentify ZIP codes in CSV files by truncating them to 3 digits, following HIPAA Safe Harbor guidelines.

## Functional Requirements

### 1. Input Processing
- Accept CSV files as input
- Support specifying which column(s) contain ZIP codes
- Handle both column names and column indices
- Support multiple ZIP code columns in a single file

### 2. ZIP Code Deidentification

#### Configuration Options

**Precision Level** (`--precision` or `-p`):
- `2`: Truncate to 2 digits (e.g., `12345` → `12000` or `12XXX`)
- `3`: Truncate to 3 digits (e.g., `12345` → `123XX` or `12300`) - **Default**
- `smart`: HIPAA-compliant smart mode - use 3 digits when population ≥ 20,000, otherwise use 2 digits

**Fill Character** (`--fill` or `-f`):
- `0`: Use zeros for replacement (e.g., `12345` → `12300` or `12000`) - **Default**
- `X`: Use X's for replacement (e.g., `12345` → `123XX` or `12XXX`)

#### Deidentification Logic

**For 2-digit precision:**
- Keep first 2 digits, replace remaining with fill character
- Examples: `12345` → `12000` (zeros) or `12XXX` (X's)

**For 3-digit precision:**
- Keep first 3 digits, replace remaining with fill character
- Examples: `12345` → `12300` (zeros) or `123XX` (X's)

**For smart precision (HIPAA Safe Harbor compliant):**
- Sparsely populated ZIP code prefixes (population < 20,000, based on 2010 Census):
  - `036, 059, 102, 203, 205, 369, 556, 692, 821, 823, 878, 879, 884, 893`
- For sparsely populated prefixes: use 2-digit precision (e.g., `03601` → `03000` or `03XXX`)
- For normal prefixes (population ≥ 20,000): use 3-digit precision (e.g., `12345` → `12300` or `123XX`)

**General Handling:**
- Handle ZIP+4 format (e.g., `12345-6789` → `123XX` or `12300`)
- Preserve empty/null values
- Handle malformed ZIP codes gracefully

### 3. Output Generation
- Generate a new CSV file with deidentified ZIP codes
- Preserve all other columns and data unchanged
- Maintain CSV structure (headers, formatting)
- Default output filename: `{original_name}_deidentified.csv`
- Allow custom output filename specification

### 4. Command-Line Interface
- Required argument: input CSV file path
- Optional arguments:
  - `-o, --output`: Custom output file path
  - `-c, --columns`: Column name(s) or index/indices containing ZIP codes (default: "zipcode")
  - `-p, --precision`: Precision level: `2`, `3`, or `smart` (default: `3`)
  - `-f, --fill`: Fill character: `0` or `X` (default: `0`)

## Non-Functional Requirements

### 1. Usability
- Clear error messages for missing files or invalid columns
- Progress/completion feedback to user
- Warning messages for columns not found

### 2. Compatibility
- Python 3.6+
- Use only standard library (no external dependencies)
- Cross-platform (Windows, macOS, Linux)

### 3. Data Integrity
- Preserve original file (never modify in-place)
- Maintain data types and encoding (UTF-8)
- Handle special characters in CSV properly

## Example Usage

```bash
# Basic usage (default: 3-digit precision with zeros)
python deidentify_zipcode.py input.csv
# Result: 12345 → 12300

# Use X's instead of zeros
python deidentify_zipcode.py input.csv -f X
# Result: 12345 → 123XX

# 2-digit precision
python deidentify_zipcode.py input.csv -p 2
# Result: 12345 → 12000

# 2-digit precision with X's
python deidentify_zipcode.py input.csv -p 2 -f X
# Result: 12345 → 12XXX

# HIPAA-compliant smart mode (3 digits when safe, 2 digits for sparse areas)
python deidentify_zipcode.py input.csv -p smart
# Result: 12345 → 12300, but 03601 → 03000

# Smart mode with X's
python deidentify_zipcode.py input.csv -p smart -f X
# Result: 12345 → 123XX, but 03601 → 03XXX

# Specify column name
python deidentify_zipcode.py input.csv -c zip_code

# Multiple columns with custom settings
python deidentify_zipcode.py input.csv -c home_zip work_zip -p smart -f X

# Custom output file
python deidentify_zipcode.py input.csv -o output.csv -c zipcode -p 3 -f 0

# Using column index (0-based)
python deidentify_zipcode.py input.csv -c 0 3 -p 2
```

## Test Cases

### 1. 3-Digit Precision with Zeros (Default)
- `12345` → `12300`
- `90210` → `90200`
- `00501` → `00500`

### 2. 3-Digit Precision with X's
- `12345` → `123XX`
- `90210` → `902XX`
- `00501` → `005XX`

### 3. 2-Digit Precision with Zeros
- `12345` → `12000`
- `90210` → `90000`
- `00501` → `00000`

### 4. 2-Digit Precision with X's
- `12345` → `12XXX`
- `90210` → `90XXX`
- `00501` → `00XXX`

### 5. Smart Mode with Zeros (HIPAA-compliant)
- `12345` → `12300` (normal population)
- `90210` → `90200` (normal population)
- `03601` → `03000` (sparse - prefix 036)
- `05901` → `05000` (sparse - prefix 059)
- `10234` → `10000` (sparse - prefix 102)
- `82101` → `82000` (sparse - prefix 821)

### 6. Smart Mode with X's (HIPAA-compliant)
- `12345` → `123XX` (normal population)
- `90210` → `902XX` (normal population)
- `03601` → `03XXX` (sparse - prefix 036)
- `05901` → `05XXX` (sparse - prefix 059)
- `82101` → `82XXX` (sparse - prefix 821)

### 7. ZIP+4 Format (all precision modes)
- `12345-6789` → `12300` / `123XX` / `12000` / `12XXX` (depending on mode)
- `90210-1234` → `90200` / `902XX` / `90000` / `90XXX` (depending on mode)

### 8. Edge Cases
- Empty values → preserve as-is
- Invalid/short ZIP codes → preserve or handle gracefully
- Non-numeric characters → strip and process

### 9. CSV Handling
- Headers preserved
- Multiple columns processed correctly
- Special characters and commas in other fields handled properly
