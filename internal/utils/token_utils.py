import math
from typing import List, Optional
from ..domain.models.document import OCRToken


def sort_tokens_by_x(tokens: List[OCRToken]) -> None:
    sort_tokens_by_x_with_tolerance(tokens, 0.01)


def sort_tokens_by_x_with_tolerance(tokens: List[OCRToken], row_tolerance: float) -> None:
    def compare_tokens(token1: OCRToken, token2: OCRToken) -> bool:
        y_diff = abs(token1.bounding_box.mid_y() - token2.bounding_box.mid_y())
        
        if y_diff < row_tolerance:
            return token1.bounding_box.x0 < token2.bounding_box.x0
        
        return token1.bounding_box.mid_y() < token2.bounding_box.mid_y()
    
    from functools import cmp_to_key
    tokens.sort(key=cmp_to_key(lambda a, b: -1 if compare_tokens(a, b) else 1))


def join_tokens_smartly(tokens: List[OCRToken]) -> str:
    if not tokens:
        return ""
    
    def is_tight_character(text: str) -> bool:
        return text in [",", ".", ":", ";", ")", "]", "%"]
    
    result_parts = []
    
    for i, token in enumerate(tokens):
        text = token.text
        if i == 0:
            result_parts.append(text)
            continue
        
        previous_text = "".join(result_parts)
        
        if (is_tight_character(text) or text in ["-", "/", "&"] or 
            previous_text.endswith("(") or previous_text.endswith("[")):
            result_parts.append(text)
        else:
            result_parts.append(" ")
            result_parts.append(text)
    
    result = "".join(result_parts)
    result = result.replace("$ ", "$")
    result = result.replace(" - ", "-")
    return result.strip()


def create_string_pointer(value: str) -> Optional[str]:
    return value.strip() if value.strip() else None