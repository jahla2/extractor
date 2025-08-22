from typing import List
from ...domain.interfaces.parser import TokenMatcher
from ...domain.models.document import OCRToken, BoundingBox


class TokenMatcherService(TokenMatcher):
    def __init__(self, tokens: List[OCRToken]):
        self.tokens = tokens
    
    def get_tokens_by_bounding_boxes(self, boxes: List[BoundingBox]) -> List[OCRToken]:
        result = []
        for token in self.tokens:
            mid_x, mid_y = token.bounding_box.mid_x(), token.bounding_box.mid_y()
            for box in boxes:
                if mid_x >= box.x0 and mid_x <= box.x1 and mid_y >= box.y0 and mid_y <= box.y1:
                    result.append(token)
                    break
        return result
    
    def get_tokens_in_bounding_box(self, box: BoundingBox) -> List[OCRToken]:
        result = []
        for token in self.tokens:
            if box.contains_center(token):
                result.append(token)
        return result