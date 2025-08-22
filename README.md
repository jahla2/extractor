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
- **Adaptive Template-Based Extraction**: Automatically adjusts extraction parameters based on document characteristics
- **Multi-Vendor Support**: Works with documents from NZ, US, and AU regions
- **Multi-Line Entry Processing**: Intelligently merges continuation lines
- **Clean Architecture**: Follows SOLID principles with dependency inversion
- **Minimal Dependencies**: Only FastAPI for web interface, pure Python for all algorithms

## Key Components

### Core Models
- `BoundingBox`: Normalized coordinate system (0.0 to 1.0)
- `OCRToken`: Text with bounding box coordinates
- `DocumentTemplate`: JSON-defined document structure
- `ExtractionResult`: Structured output with header and lines

### Adaptive Algorithm
- Analyzes document characteristics (row spacing, density, variability)
- Calculates optimal thresholds dynamically
- Supports Voronoi-like column stretching
- Handles irregular document layouts

### Multi-Line Processing
- Detects continuation patterns for NZ/US/AU documents
- Recognizes date formats, currency patterns, reference numbers
- Smart text merging with continuation markers

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