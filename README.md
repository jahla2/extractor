# OCR Extractor - Python Implementation

A pure Python OCR document extraction service featuring lightweight algorithms, zero external dependencies for core processing, and fast template-based extraction.

## Architecture

The system follows Clean Architecture principles with clear separation of concerns:

```
internal/
├── domain/
│   ├── models/          # Domain entities and data structures
│   └── interfaces/      # Abstract base classes defining contracts
├── application/
│   └── services/        # Business logic implementations
├── infrastructure/
│   ├── config/          # Configuration and document analysis
│   ├── factory/         # Dependency injection factory
│   └── parsers/         # Template and OCR data parsers
├── presentation/
│   └── handlers/        # FastAPI HTTP handlers
└── utils/
    └── token_utils.py   # Token processing utilities
```

## Features

- **Pure Algorithm Implementation**: Core extraction uses only Python standard library (math, json, re)
- **Lightweight & Fast**: Zero external dependencies for processing algorithms

### Advanced Extraction Algorithms

- **Adaptive Template-Based Extraction**: Dynamically calculates row tolerances, column stretching, and header padding based on document density, spacing variability, and layout characteristics

- **Voronoi-Style Column Stretching**: When multi-line content overflows, columns intelligently expand into adjacent empty spaces using stretch factors (0.75-0.95) based on column count and document density

- **Multi-Line Entry Processing**: 
  - Detects continuation lines with fewer meaningful fields than parent lines
  - Recognizes structured data (dates: dd/mm/yyyy, currency: $, AUD, reference codes: INV-, PO-)
  - Merges text with continuation markers (&, comma, ellipsis, semicolon, backslash)
  - Smart text joining with proper spacing and marker removal

- **Document Region Analysis**: 
  - Auto-detects header (0-25%), data (25-80%), footer (80-100%) regions
  - Calculates token distribution and density per region
  - Adapts extraction parameters based on regional characteristics

- **Multi-Vendor Document Support**: Optimized patterns for NZ, US, and AU document formats including currency symbols, date formats, and reference number patterns

- **Clean Architecture**: Follows SOLID principles with dependency inversion
- **Minimal Dependencies**: Only FastAPI for web interface, pure Python for all algorithms

## Key Components

### Core Models
- `BoundingBox`: Normalized coordinate system (0.0 to 1.0)
- `OCRToken`: Text with bounding box coordinates
- `DocumentTemplate`: JSON-defined document structure
- `ExtractionResult`: Structured output with header and lines

### Adaptive Algorithm Details
- **Document Characteristics Analysis**: 
  - Row spacing statistics (average, median, min/max, variability coefficient)
  - Column width calculations and document density metrics
  - Header height detection and line count estimation
- **Dynamic Threshold Calculation**:
  - Row tolerance: `median_spacing * 0.5` (adjusted for variability 0.005-0.025 range)
  - Column stretch: Base 0.85, reduced to 0.75 for >6 columns, increased to 0.95 for <4 columns
  - Header padding: `avg_row_spacing * 0.3` with minimum based on header height

### Multi-Line Processing Details
- **Continuation Detection**: Lines with fewer non-empty fields than predecessor
- **Structured Field Recognition**:
  - Date patterns: "/" or "-" with digits, "." in single words
  - Currency: $¢€£¥, USD/AUD/NZD/CAD codes, decimal/comma separators
  - Reference fields: alphanumeric with INV/PO/REF/IV prefixes, or 6+ char codes
- **Smart Text Merging**:
  - Continuation markers: &, comma, -, ..., ;, :, \, /, +, "cont", "continued", "(cont)"
  - Marker-specific joining: & removes marker + space, comma/dash direct append
  - Ellipsis trimming, colon/semicolon space addition

## Installation

1. Install minimal dependencies (only for web server):
```bash
pip install -r requirements.txt
```

**Note**: Core extraction algorithms use only Python standard library - no external dependencies required for processing.

2. Run the server:
```bash
python main.py
```

## API Usage

### Health Check
```bash
curl http://localhost:8080/health
```

### Document Extraction
```bash
curl -X POST http://localhost:8080/extract-files \
  -H "Content-Type: application/json" \
  -d '{
    "llm_res_txt": "path/to/template.json",
    "new_ocr_coord_json": "path/to/ocr_tokens.txt"
  }'
```

## Environment Variables

Fine-tuning parameters (optional):
```bash
ROW_TOL_Y=0.012        # Base row tolerance (fraction of page height)
COL_STRETCH=0.90       # Column stretch factor (0.0-1.0)
HEADER_PAD_Y=0.003     # Header padding (fraction of page height)
```

## Dependencies

**Minimal External Dependencies:**
- `fastapi==0.104.1` - Web framework (API endpoints only)
- `uvicorn==0.24.0` - ASGI server (web server only)  
- `python-multipart==0.0.6` - HTTP multipart support

**Core Processing:** Pure Python standard library only (`math`, `json`, `re`, `os`, `pathlib`, `dataclasses`, `typing`)

## Testing

The system can be tested with template JSON files and OCR token data files.