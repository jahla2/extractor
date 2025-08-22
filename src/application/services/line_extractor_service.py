import math
from dataclasses import dataclass
from typing import List
from ...domain.interfaces.parser import LineExtractor, LineProcessor
from ...domain.models.document import DocumentTemplate, OCRToken, ColumnSpecification
from ...domain.models.output import OrderedFieldMap
from ...infrastructure.config.adaptive_extraction_config import AdaptiveExtractionConfiguration
from ...utils.token_utils import sort_tokens_by_x_with_tolerance, join_tokens_smartly, create_string_pointer


@dataclass
class ColumnBand:
    canonical_name: str
    x0: float
    x1: float


class LineExtractorService(LineExtractor):
    def __init__(self, template: DocumentTemplate, tokens: List[OCRToken], line_processor: LineProcessor):
        self.template = template
        self.tokens = tokens
        self.configuration = AdaptiveExtractionConfiguration()
        self.configuration.analyze_and_configure(tokens, template)
        self.line_processor = line_processor
    
    def extract_lines(self) -> List[OrderedFieldMap]:
        if not self.template.columns:
            return []
        
        columns = sorted(self.template.columns, key=lambda c: c.get_bounding_box().x0)
        column_bands = self._build_column_bands(columns)
        candidate_tokens = self._filter_candidate_tokens(column_bands, 0)
        token_rows = self._cluster_tokens_by_rows(candidate_tokens)
        raw_lines = self._build_raw_lines(token_rows, column_bands)
        
        return self.line_processor.merge_multi_line_entries(raw_lines, columns)
    
    def _build_column_bands(self, columns: List[ColumnSpecification]) -> List[ColumnBand]:
        bands = []
        for i, column in enumerate(columns):
            current_box = column.get_bounding_box()
            x0 = current_box.x0
            x1 = 1.0
            
            if i < len(columns) - 1:
                next_x0 = columns[i + 1].get_bounding_box().x0
                x1 = x0 + self.configuration.get_column_stretch() * (next_x0 - x0)
                if x1 <= x0:
                    x1 = next_x0
                if x1 > next_x0:
                    x1 = next_x0
            
            bands.append(ColumnBand(
                canonical_name=column.canonical,
                x0=x0,
                x1=x1
            ))
        
        return bands
    
    def _calculate_header_threshold(self, columns: List[ColumnSpecification]) -> float:
        header_y = 0.0
        for column in columns:
            y = column.get_bounding_box().y1
            if y > header_y:
                header_y = y
        return header_y + self.configuration.get_header_padding_y()
    
    def _get_data_region_bounds(self) -> tuple[float, float]:
        if self.configuration.is_adaptive():
            return self.configuration.data_region_start(), self.configuration.data_region_end()
        
        header_y = self._calculate_header_threshold(self.template.columns)
        return header_y, 0.75
    
    def _filter_candidate_tokens(self, bands: List[ColumnBand], header_y_threshold: float) -> List[OCRToken]:
        min_x = bands[0].x0
        max_x = bands[-1].x1
        candidates = []
        
        min_y, max_y = self._get_data_region_bounds()
        
        for token in self.tokens:
            mid_x, mid_y = token.bounding_box.mid_x(), token.bounding_box.mid_y()
            if min_y <= mid_y <= max_y and min_x <= mid_x <= max_x:
                candidates.append(token)
        
        return candidates
    
    def _cluster_tokens_by_rows(self, tokens: List[OCRToken]) -> List[List[OCRToken]]:
        if not tokens:
            return []
        
        sorted_tokens = sorted(tokens, key=lambda t: t.bounding_box.mid_y())
        
        rows = []
        current_row = [sorted_tokens[0]]
        average_y = sorted_tokens[0].bounding_box.mid_y()
        
        for token in sorted_tokens[1:]:
            token_y = token.bounding_box.mid_y()
            
            if abs(token_y - average_y) <= self.configuration.get_row_tolerance_y():
                current_row.append(token)
                average_y = (average_y * (len(current_row) - 1) + token_y) / len(current_row)
            else:
                sort_tokens_by_x_with_tolerance(current_row, self.configuration.get_row_tolerance_y())
                rows.append(current_row)
                current_row = [token]
                average_y = token_y
        
        sort_tokens_by_x_with_tolerance(current_row, self.configuration.get_row_tolerance_y())
        rows.append(current_row)
        
        return rows
    
    def _build_raw_lines(self, rows: List[List[OCRToken]], bands: List[ColumnBand]) -> List[OrderedFieldMap]:
        raw_lines = []
        
        for row in rows:
            keys = [band.canonical_name for band in bands]
            values = {}
            
            for band in bands:
                column_tokens = self._select_tokens_by_x_band(row, band.x0, band.x1)
                sort_tokens_by_x_with_tolerance(column_tokens, self.configuration.get_row_tolerance_y())
                text = join_tokens_smartly(column_tokens)
                
                if text.strip():
                    values[band.canonical_name] = create_string_pointer(text)
                else:
                    values[band.canonical_name] = None
            
            line = OrderedFieldMap(keys=keys, values=values)
            
            if not self._is_all_fields_empty(line):
                raw_lines.append(line)
        
        return raw_lines
    
    def _select_tokens_by_x_band(self, tokens: List[OCRToken], x0: float, x1: float) -> List[OCRToken]:
        result = []
        for token in tokens:
            mid_x = token.bounding_box.mid_x()
            if x0 <= mid_x <= x1:
                result.append(token)
        return result
    
    def _is_all_fields_empty(self, line: OrderedFieldMap) -> bool:
        for value in line.values.values():
            if value and value.strip():
                return False
        return True