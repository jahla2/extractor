from abc import ABC, abstractmethod
from typing import List
from ..models.document import DocumentTemplate, OCRToken
from ..models.output import ExtractionResult, DocumentHeader, OrderedFieldMap
from ..models.document import BoundingBox, ColumnSpecification


class DocumentTemplateParser(ABC):
    @abstractmethod
    def parse_document_template(self, data: bytes) -> DocumentTemplate:
        pass


class OCRDataParser(ABC):
    @abstractmethod
    def parse_ocr_tokens(self, data: str) -> List[OCRToken]:
        pass


class DocumentExtractor(ABC):
    @abstractmethod
    def extract_document(self) -> ExtractionResult:
        pass


class HeaderExtractor(ABC):
    @abstractmethod
    def extract_header(self) -> DocumentHeader:
        pass


class LineExtractor(ABC):
    @abstractmethod
    def extract_lines(self) -> List[OrderedFieldMap]:
        pass


class TokenMatcher(ABC):
    @abstractmethod
    def get_tokens_by_bounding_boxes(self, boxes: List[BoundingBox]) -> List[OCRToken]:
        pass
    
    @abstractmethod
    def get_tokens_in_bounding_box(self, box: BoundingBox) -> List[OCRToken]:
        pass


class LineProcessor(ABC):
    @abstractmethod
    def merge_multi_line_entries(self, lines: List[OrderedFieldMap], columns: List[ColumnSpecification]) -> List[OrderedFieldMap]:
        pass