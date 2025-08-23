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

- **Smart Template Adaptation**: Automatically adjusts how strictly it follows templates based on how messy or clean the document is

- **Voronoi Column Stretching**: When text is too long for a column, it smartly stretches into the next empty column to grab the complete text, like expanding a box to fit longer content

- **Multi-Line Text Merging**: 
  - Spots when text continues on the next line (like addresses or descriptions)
  - Recognizes important data types (dates, money amounts, invoice numbers)
  - Joins split text back together with proper spacing
  - Handles continuation symbols (like & or ... at the end of lines)

- **Document Layout Detection**: 
  - Automatically finds header area, main data section, and footer
  - Learns each section's text patterns and density
  - Adjusts extraction rules for each section type

- **Multi-Country Format Support**: Understands different document styles from New Zealand, US, and Australia including their currency symbols, date formats, and business reference patterns

- **Clean Architecture**: Follows SOLID principles with dependency inversion
- **Minimal Dependencies**: Only FastAPI for web interface, pure Python for all algorithms

## Key Components

### Core Models
- `BoundingBox`: Normalized coordinate system (0.0 to 1.0)
- `OCRToken`: Text with bounding box coordinates
- `DocumentTemplate`: JSON-defined document structure
- `ExtractionResult`: Structured output with header and lines

### How the Smart Algorithms Work

**Document Analysis Process**:
- Measures how much space is between rows and how consistent it is
- Calculates how wide columns are and how packed with text the document is
- Figures out where the header ends and data begins

**Adaptive Rules**:
- For messy documents with inconsistent spacing: becomes more flexible with alignment
- For documents with many narrow columns: stretches less to avoid overlap
- For documents with few wide columns: stretches more to capture long text
- Adjusts header detection based on how much text is at the top

**Multi-Line Text Handling**:
- Spots continuation lines by counting how many fields have data (fewer = likely continuation)
- Recognizes structured data like dates (slashes/dashes), money (dollar signs), invoice numbers (starts with INV/PO)
- Joins text intelligently based on continuation symbols:
  - Ampersand (&): removes symbol and adds space
  - Commas/dashes: joins directly without space
  - Ellipsis (...): removes dots and adds space
  - Colons/semicolons: keeps symbol and adds space

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