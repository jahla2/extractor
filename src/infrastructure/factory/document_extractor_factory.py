import os
from pathlib import Path
from ...domain.interfaces.parser import DocumentTemplateParser, OCRDataParser, DocumentExtractor
from ...application.services.document_extractor_service import DocumentExtractorService
from ...application.services.header_extractor_service import HeaderExtractorService
from ...application.services.line_extractor_service import LineExtractorService
from ...application.services.line_processor_service import LineProcessorService
from ...application.services.token_matcher_service import TokenMatcherService
from ...infrastructure.config.adaptive_extraction_config import AdaptiveExtractionConfiguration


class ExtractionRequest:
    def __init__(self, llm_res_txt: str, new_ocr_coord_json: str):
        self.llm_template_path = llm_res_txt
        self.normalized_ocr_path = new_ocr_coord_json


def create_document_extractor(
    template_parser: DocumentTemplateParser, 
    ocr_parser: OCRDataParser, 
    request: ExtractionRequest
) -> DocumentExtractor:
    
    # Read template file
    template_path = Path(request.llm_template_path)
    with open(template_path, 'rb') as f:
        template_data = f.read()
    
    template = template_parser.parse_document_template(template_data)
    
    # Read OCR data file
    ocr_path = Path(request.normalized_ocr_path)
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_data = f.read()
    
    tokens = ocr_parser.parse_ocr_tokens(ocr_data)
    
    # Create token matcher
    token_matcher = TokenMatcherService(tokens)
    
    # Create adaptive config to get row tolerance
    adaptive_config = AdaptiveExtractionConfiguration()
    adaptive_config.analyze_and_configure(tokens, template)
    row_tolerance = adaptive_config.get_row_tolerance_y()
    
    # Create extractors
    header_extractor = HeaderExtractorService(template, token_matcher, row_tolerance)
    line_processor = LineProcessorService()
    line_extractor = LineExtractorService(template, tokens, line_processor)
    
    return DocumentExtractorService(header_extractor, line_extractor)