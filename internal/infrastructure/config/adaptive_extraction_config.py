from typing import List, Optional
from ...domain.models.document import OCRToken, DocumentTemplate
from ...domain.models.analysis import AdaptiveThresholds
from .document_analyzer_service import DocumentAnalyzerService
from .extraction_config import ExtractionConfiguration


class AdaptiveExtractionConfiguration:
    def __init__(self):
        self.analyzer = DocumentAnalyzerService()
        self.static_config = ExtractionConfiguration()
        self.adaptive_thresholds: Optional[AdaptiveThresholds] = None
    
    def analyze_and_configure(self, tokens: List[OCRToken], template: DocumentTemplate) -> None:
        characteristics = self.analyzer.analyze_document_characteristics(tokens, template)
        self.adaptive_thresholds = self.analyzer.calculate_adaptive_thresholds(characteristics)
    
    def get_row_tolerance_y(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.row_tolerance_y
        return self.static_config.row_tolerance_y
    
    def get_column_stretch(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.column_stretch
        return self.static_config.column_stretch
    
    def get_header_padding_y(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.header_padding_y
        return self.static_config.header_padding_y
    
    def get_multi_line_threshold(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.multi_line_threshold
        return 0.008
    
    def is_adaptive(self) -> bool:
        return self.adaptive_thresholds is not None
    
    def data_region_start(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.data_region_start
        return 0.25
    
    def data_region_end(self) -> float:
        if self.adaptive_thresholds:
            return self.adaptive_thresholds.data_region_end
        return 0.80