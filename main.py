import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from internal.infrastructure.parsers.document_template_parser import DocumentTemplateParserImpl
from internal.infrastructure.parsers.ocr_data_parser import OCRDataParserImpl
from internal.infrastructure.factory.document_extractor_factory import create_document_extractor
from internal.presentation.handlers.extraction_handler import ExtractionHandler
from internal.presentation.handlers.health_handler import HealthHandler


class ApplicationDependencies:
    def __init__(self):
        self.health_handler = HealthHandler()
        self.extraction_handler = self._create_extraction_handler()
    
    def _create_extraction_handler(self) -> ExtractionHandler:
        template_parser = DocumentTemplateParserImpl()
        ocr_parser = OCRDataParserImpl()
        
        return ExtractionHandler(
            template_parser=template_parser,
            ocr_parser=ocr_parser,
            extractor_factory=create_document_extractor
        )


def wire_application_dependencies() -> ApplicationDependencies:
    return ApplicationDependencies()


def setup_fastapi_server(dependencies: ApplicationDependencies) -> FastAPI:
    app = FastAPI(
        title="OCR Extractor API",
        description="Adaptive template-based OCR document extraction service",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        return await dependencies.health_handler.handle_health_check()
    
    @app.post("/extract-files")
    async def extract_files(request_data: dict):
        return await dependencies.extraction_handler.handle_extract_files(request_data)
    
    return app


def start_server():
    import uvicorn
    dependencies = wire_application_dependencies()
    app = setup_fastapi_server(dependencies)
    
    server_port = 8080
    logging.info(f"Server listening on port {server_port}")
    
    uvicorn.run(app, host="0.0.0.0", port=server_port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()