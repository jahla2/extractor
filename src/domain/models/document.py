from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json


@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float
    
    def mid_x(self) -> float:
        return (self.x0 + self.x1) / 2
    
    def mid_y(self) -> float:
        return (self.y0 + self.y1) / 2
    
    def contains_center(self, token: 'OCRToken') -> bool:
        mid_x, mid_y = token.bounding_box.mid_x(), token.bounding_box.mid_y()
        return mid_x >= self.x0 and mid_x <= self.x1 and mid_y >= self.y0 and mid_y <= self.y1


@dataclass
class OCRToken:
    text: str
    bounding_box: BoundingBox


@dataclass
class FieldSpecification:
    value: Optional[str] = None
    token_bboxes: Optional[List[List[float]]] = None
    bbox: Optional[List[float]] = None
    
    def get_bounding_box(self) -> tuple[Optional[BoundingBox], bool]:
        if self.bbox and len(self.bbox) == 4:
            return BoundingBox(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3]), True
        return None, False
    
    def get_token_bounding_boxes(self) -> List[BoundingBox]:
        if not self.token_bboxes:
            return []
        result = []
        for coords in self.token_bboxes:
            if len(coords) == 4:
                result.append(BoundingBox(coords[0], coords[1], coords[2], coords[3]))
        return result


@dataclass
class ColumnSpecification:
    source: str
    canonical: str
    bbox: List[float]
    token_bboxes: Optional[List[List[float]]] = None
    
    def get_bounding_box(self) -> BoundingBox:
        return BoundingBox(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])


@dataclass
class DocumentTemplate:
    header: Dict[str, FieldSpecification]
    columns: List[ColumnSpecification]