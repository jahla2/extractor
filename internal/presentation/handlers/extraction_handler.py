import json
from typing import Callable
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from ...domain.interfaces.parser import DocumentTemplateParser, OCRDataParser, DocumentExtractor
from ...infrastructure.factory.document_extractor_factory import ExtractionRequest


class ExtractionHandler:
    def __init__(
        self, 
        template_parser: DocumentTemplateParser,
        ocr_parser: OCRDataParser,
        extractor_factory: Callable[[DocumentTemplateParser, OCRDataParser, ExtractionRequest], DocumentExtractor]
    ):
        self.template_parser = template_parser
        self.ocr_parser = ocr_parser
        self.document_extractor = extractor_factory
    
    async def handle_extract_files(self, request_data: dict) -> JSONResponse:
        try:
            # Validate required fields
            if 'llm_res_txt' not in request_data or 'new_ocr_coord_json' not in request_data:
                raise HTTPException(
                    status_code=400, 
                    detail="llm_res_txt and new_ocr_coord_json are required file paths"
                )
            
            extraction_request = ExtractionRequest(
                llm_res_txt=request_data['llm_res_txt'],
                new_ocr_coord_json=request_data['new_ocr_coord_json']
            )
            
            # Create document extractor
            try:
                extractor = self.document_extractor(
                    self.template_parser, 
                    self.ocr_parser, 
                    extraction_request
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"extraction setup failed: {str(e)}"
                )
            
            # Extract document
            result = extractor.extract_document()
            
            return JSONResponse(
                content=result.to_dict(),
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    def _escape_error(self, error: Exception) -> str:
        error_message = str(error)
        try:
            escaped_bytes = json.dumps(error_message)
            return escaped_bytes[1:-1]  # Remove surrounding quotes
        except:
            return error_message