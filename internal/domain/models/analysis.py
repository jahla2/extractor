from dataclasses import dataclass


@dataclass
class DocumentRegion:
    start_y: float
    end_y: float
    token_count: int
    density: float
    percentage: float


@dataclass
class DocumentRegions:
    header_region: DocumentRegion
    data_region: DocumentRegion
    footer_region: DocumentRegion


@dataclass
class DocumentCharacteristics:
    average_row_spacing: float
    median_row_spacing: float
    min_row_spacing: float
    max_row_spacing: float
    average_column_width: float
    header_height: float
    document_density: float
    line_count: int
    column_count: int
    spacing_variability: float
    document_regions: DocumentRegions


@dataclass
class AdaptiveThresholds:
    row_tolerance_y: float
    column_stretch: float
    header_padding_y: float
    multi_line_threshold: float
    data_region_start: float
    data_region_end: float