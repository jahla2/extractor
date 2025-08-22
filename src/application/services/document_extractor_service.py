from ...domain.interfaces.parser import DocumentExtractor, HeaderExtractor, LineExtractor
from ...domain.models.output import ExtractionResult


class DocumentExtractorService(DocumentExtractor):
    def __init__(self, header_extractor: HeaderExtractor, line_extractor: LineExtractor):
        self.header_extractor = header_extractor
        self.line_extractor = line_extractor
    
    def extract_document(self) -> ExtractionResult:
        header = self.header_extractor.extract_header()
        lines = self.line_extractor.extract_lines()
        
        return ExtractionResult(
            header=header,
            lines=lines
        )