import math
from typing import List, Dict
from ...domain.models.document import OCRToken, DocumentTemplate
from ...domain.models.analysis import DocumentCharacteristics, AdaptiveThresholds, DocumentRegions, DocumentRegion


class DocumentAnalyzerService:
    def __init__(self):
        pass
    
    def analyze_document_characteristics(self, tokens: List[OCRToken], template: DocumentTemplate) -> DocumentCharacteristics:
        if not tokens:
            return self._get_default_characteristics()
        
        sorted_by_y = sorted(tokens, key=lambda t: t.bounding_box.mid_y())
        
        row_spacings = self._calculate_row_spacings(sorted_by_y)
        column_widths = self._calculate_column_widths(template)
        header_height = self._calculate_header_height(template)
        density = self._calculate_document_density(tokens)
        variability = self._calculate_spacing_variability(row_spacings)
        document_regions = self._analyze_document_regions(sorted_by_y, template)
        
        return DocumentCharacteristics(
            average_row_spacing=self._calculate_average(row_spacings),
            median_row_spacing=self._calculate_median(row_spacings),
            min_row_spacing=self._calculate_min(row_spacings),
            max_row_spacing=self._calculate_max(row_spacings),
            average_column_width=self._calculate_average(column_widths),
            header_height=header_height,
            document_density=density,
            line_count=self._estimate_line_count(sorted_by_y),
            column_count=len(template.columns),
            spacing_variability=variability,
            document_regions=document_regions
        )
    
    def calculate_adaptive_thresholds(self, characteristics: DocumentCharacteristics) -> AdaptiveThresholds:
        row_tolerance = self._calculate_adaptive_row_tolerance(characteristics)
        column_stretch = self._calculate_adaptive_column_stretch(characteristics)
        header_padding = self._calculate_adaptive_header_padding(characteristics)
        multi_line_threshold = self._calculate_multi_line_threshold(characteristics)
        
        return AdaptiveThresholds(
            row_tolerance_y=row_tolerance,
            column_stretch=column_stretch,
            header_padding_y=header_padding,
            multi_line_threshold=multi_line_threshold,
            data_region_start=characteristics.document_regions.data_region.start_y,
            data_region_end=characteristics.document_regions.data_region.end_y
        )
    
    def _calculate_row_spacings(self, sorted_tokens: List[OCRToken]) -> List[float]:
        if len(sorted_tokens) < 2:
            return [0.012]
        
        spacings = []
        for i in range(1, len(sorted_tokens)):
            spacing = abs(sorted_tokens[i].bounding_box.mid_y() - sorted_tokens[i-1].bounding_box.mid_y())
            if spacing > 0.001:
                spacings.append(spacing)
        
        if not spacings:
            return [0.012]
        
        # Remove outliers
        spacings.sort()
        start = int(len(spacings) * 0.1)
        end = int(len(spacings) * 0.9)
        if start >= end:
            return spacings
        return spacings[start:end]
    
    def _calculate_column_widths(self, template: DocumentTemplate) -> List[float]:
        if not template.columns:
            return [0.2]
        
        widths = []
        for col in template.columns:
            bbox = col.get_bounding_box()
            widths.append(bbox.x1 - bbox.x0)
        return widths
    
    def _calculate_header_height(self, template: DocumentTemplate) -> float:
        max_y = 0.0
        for field in template.header.values():
            bbox, has_box = field.get_bounding_box()
            if has_box and bbox:
                if bbox.y1 > max_y:
                    max_y = bbox.y1
        
        for col in template.columns:
            bbox = col.get_bounding_box()
            if bbox.y1 > max_y:
                max_y = bbox.y1
        
        return max_y
    
    def _calculate_document_density(self, tokens: List[OCRToken]) -> float:
        if not tokens:
            return 0.5
        
        total_area = 0.0
        for token in tokens:
            bbox = token.bounding_box
            area = (bbox.x1 - bbox.x0) * (bbox.y1 - bbox.y0)
            total_area += area
        
        return total_area / 1.0
    
    def _calculate_spacing_variability(self, spacings: List[float]) -> float:
        if len(spacings) < 2:
            return 0.0
        
        mean = self._calculate_average(spacings)
        variance = sum((s - mean) ** 2 for s in spacings) / len(spacings)
        return math.sqrt(variance) / mean
    
    def _estimate_line_count(self, sorted_tokens: List[OCRToken]) -> int:
        if not sorted_tokens:
            return 0
        
        current_y = sorted_tokens[0].bounding_box.mid_y()
        line_count = 1
        tolerance = 0.01
        
        for token in sorted_tokens[1:]:
            token_y = token.bounding_box.mid_y()
            if abs(token_y - current_y) > tolerance:
                line_count += 1
                current_y = token_y
        
        return line_count
    
    def _calculate_adaptive_row_tolerance(self, characteristics: DocumentCharacteristics) -> float:
        base = characteristics.median_row_spacing * 0.5
        
        if characteristics.spacing_variability > 0.3:
            base *= 1.5
        elif characteristics.spacing_variability < 0.1:
            base *= 0.8
        
        return max(0.005, min(base, 0.025))
    
    def _calculate_adaptive_column_stretch(self, characteristics: DocumentCharacteristics) -> float:
        base = 0.85
        
        if characteristics.column_count > 6:
            base = 0.75
        elif characteristics.column_count < 4:
            base = 0.95
        
        if characteristics.document_density > 0.3:
            base *= 0.9
        
        return base
    
    def _calculate_adaptive_header_padding(self, characteristics: DocumentCharacteristics) -> float:
        base = characteristics.average_row_spacing * 0.3
        min_padding = characteristics.header_height * 0.02
        
        if base < min_padding:
            base = min_padding
        
        return max(0.001, min(base, 0.01))
    
    def _calculate_multi_line_threshold(self, characteristics: DocumentCharacteristics) -> float:
        return characteristics.median_row_spacing * 0.7
    
    def _calculate_average(self, values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0
    
    def _calculate_median(self, values: List[float]) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    def _calculate_min(self, values: List[float]) -> float:
        return min(values) if values else 0.0
    
    def _calculate_max(self, values: List[float]) -> float:
        return max(values) if values else 0.0
    
    def _get_default_characteristics(self) -> DocumentCharacteristics:
        return DocumentCharacteristics(
            average_row_spacing=0.012,
            median_row_spacing=0.012,
            min_row_spacing=0.008,
            max_row_spacing=0.020,
            average_column_width=0.15,
            header_height=0.1,
            document_density=0.3,
            line_count=10,
            column_count=5,
            spacing_variability=0.2,
            document_regions=DocumentRegions(
                header_region=DocumentRegion(start_y=0.0, end_y=0.25, token_count=0, density=0.0, percentage=25.0),
                data_region=DocumentRegion(start_y=0.25, end_y=0.80, token_count=0, density=0.0, percentage=55.0),
                footer_region=DocumentRegion(start_y=0.80, end_y=1.0, token_count=0, density=0.0, percentage=20.0)
            )
        )
    
    def _analyze_document_regions(self, tokens: List[OCRToken], template: DocumentTemplate) -> DocumentRegions:
        if not tokens:
            return self._get_default_characteristics().document_regions
        
        buckets = self._analyze_token_distribution(tokens)
        column_start, column_end = self._get_column_boundaries(template)
        
        header_region = self._detect_header_region(buckets, column_start)
        data_region = self._detect_data_region(buckets, column_start, column_end)
        footer_region = self._detect_footer_region(buckets, data_region.end_y)
        
        return DocumentRegions(
            header_region=header_region,
            data_region=data_region,
            footer_region=footer_region
        )
    
    def _analyze_token_distribution(self, tokens: List[OCRToken]) -> Dict[int, int]:
        buckets = {}
        for token in tokens:
            y_bucket = int(token.bounding_box.mid_y() * 100)
            buckets[y_bucket] = buckets.get(y_bucket, 0) + 1
        return buckets
    
    def _get_column_boundaries(self, template: DocumentTemplate) -> tuple[float, float]:
        if not template.columns:
            return 0.25, 0.80
        
        min_y = 1.0
        max_y = 0.0
        
        for col in template.columns:
            bbox = col.get_bounding_box()
            min_y = min(min_y, bbox.y0)
            max_y = max(max_y, bbox.y1)
        
        return min_y, max_y + 0.05
    
    def _detect_header_region(self, buckets: Dict[int, int], column_start: float) -> DocumentRegion:
        header_end = column_start
        token_count = sum(count for y_bucket, count in buckets.items() 
                         if float(y_bucket) / 100.0 < header_end)
        
        percentage = header_end * 100
        density = token_count / header_end if header_end > 0 else 0
        
        return DocumentRegion(
            start_y=0.0,
            end_y=header_end,
            token_count=token_count,
            density=density,
            percentage=percentage
        )
    
    def _detect_data_region(self, buckets: Dict[int, int], column_start: float, column_end: float) -> DocumentRegion:
        data_end = self._find_data_region_end(buckets, column_end)
        token_count = sum(count for y_bucket, count in buckets.items() 
                         if column_start <= float(y_bucket) / 100.0 < data_end)
        
        region_height = data_end - column_start
        percentage = region_height * 100
        density = token_count / region_height if region_height > 0 else 0
        
        return DocumentRegion(
            start_y=column_start,
            end_y=data_end,
            token_count=token_count,
            density=density,
            percentage=percentage
        )
    
    def _find_data_region_end(self, buckets: Dict[int, int], column_end: float) -> float:
        y_positions = [y_bucket for y_bucket in buckets.keys() 
                      if float(y_bucket) / 100.0 > column_end]
        
        if not y_positions:
            return 0.80
        
        y_positions.sort()
        
        max_gap = 0
        data_end_bucket = int(0.80 * 100)
        
        for i in range(1, len(y_positions)):
            gap = y_positions[i] - y_positions[i-1]
            if gap > max_gap and gap > 5:
                max_gap = gap
                data_end_bucket = y_positions[i-1] + 2
        
        data_end = float(data_end_bucket) / 100.0
        
        if data_end < column_end + 0.05:
            data_end = 0.80
        if data_end > 0.95:
            data_end = 0.95
        
        return data_end
    
    def _detect_footer_region(self, buckets: Dict[int, int], data_end: float) -> DocumentRegion:
        token_count = sum(count for y_bucket, count in buckets.items() 
                         if float(y_bucket) / 100.0 >= data_end)
        
        region_height = 1.0 - data_end
        percentage = region_height * 100
        density = token_count / region_height if region_height > 0 else 0
        
        return DocumentRegion(
            start_y=data_end,
            end_y=1.0,
            token_count=token_count,
            density=density,
            percentage=percentage
        )