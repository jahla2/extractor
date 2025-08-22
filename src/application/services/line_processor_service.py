import re
from typing import List
from ...domain.interfaces.parser import LineProcessor
from ...domain.models.output import OrderedFieldMap
from ...domain.models.document import ColumnSpecification
from ...utils.token_utils import create_string_pointer


class LineProcessorService(LineProcessor):
    def __init__(self):
        pass
    
    def merge_multi_line_entries(self, lines: List[OrderedFieldMap], columns: List[ColumnSpecification]) -> List[OrderedFieldMap]:
        if len(lines) <= 1:
            return lines
        
        result = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i]
            continuation_lines = self._find_continuation_lines(lines, i, columns)
            
            if continuation_lines:
                merged_line = self._merge_lines_content(current_line, continuation_lines, columns)
                result.append(merged_line)
                i += len(continuation_lines) + 1
            else:
                result.append(current_line)
                i += 1
        
        return result
    
    def _find_continuation_lines(self, lines: List[OrderedFieldMap], start_index: int, columns: List[ColumnSpecification]) -> List[OrderedFieldMap]:
        if start_index >= len(lines) - 1:
            return []
        
        continuations = []
        current_line = lines[start_index]
        
        for i in range(start_index + 1, len(lines)):
            next_line = lines[i]
            
            if self._is_continuation_line(current_line, next_line, columns):
                continuations.append(next_line)
            else:
                break
        
        return continuations
    
    def _is_continuation_line(self, current_line: OrderedFieldMap, next_line: OrderedFieldMap, columns: List[ColumnSpecification]) -> bool:
        current_non_empty = self._count_non_empty_fields(current_line)
        next_non_empty = self._count_non_empty_fields(next_line)
        
        if next_non_empty >= current_non_empty:
            return False
        
        meaningful_fields = 0
        for column in columns:
            if next_line.values:
                value = next_line.values.get(column.canonical)
                if value:
                    text = value.strip()
                    if self._is_structured_field(text):
                        meaningful_fields += 1
        
        return meaningful_fields <= 1
    
    def _merge_lines_content(self, current_line: OrderedFieldMap, continuations: List[OrderedFieldMap], columns: List[ColumnSpecification]) -> OrderedFieldMap:
        merged = OrderedFieldMap(
            keys=current_line.keys.copy(),
            values=current_line.values.copy() if current_line.values else {}
        )
        
        for continuation_line in continuations:
            for column in columns:
                key = column.canonical
                current_value = merged.values.get(key)
                continuation_value = continuation_line.values.get(key)
                
                if current_value and continuation_value:
                    current_text = current_value.strip()
                    continuation_text = continuation_value.strip()
                    
                    if continuation_text:
                        if self._has_continuation_marker(current_text):
                            merged.values[key] = create_string_pointer(self._merge_continuation_text(current_text, continuation_text))
                        else:
                            merged.values[key] = create_string_pointer(f"{current_text} {continuation_text}")
                elif not current_value and continuation_value:
                    merged.values[key] = continuation_value
        
        return merged
    
    def _count_non_empty_fields(self, line: OrderedFieldMap) -> int:
        count = 0
        for value in line.values.values():
            if value and value.strip():
                count += 1
        return count
    
    def _is_structured_field(self, text: str) -> bool:
        if not text:
            return False
        
        if self._is_date_field(text):
            return True
        
        if self._is_currency_field(text):
            return True
        
        if self._is_reference_field(text):
            return True
        
        if len(text.split()) == 1 and len(text) >= 3:
            return True
        
        return False
    
    def _is_date_field(self, text: str) -> bool:
        return ("/" in text or 
                ("-" in text and any(c.isdigit() for c in text)) or
                ("." in text and len(text.split()) == 1))
    
    def _is_currency_field(self, text: str) -> bool:
        return (any(symbol in text for symbol in "$¢€£¥") or
                any(code in text for code in ["USD", "AUD", "NZD", "CAD"]) or
                (any(c.isdigit() for c in text) and any(sep in text for sep in [".", ","])))
    
    def _is_reference_field(self, text: str) -> bool:
        upper_text = text.upper()
        return (any(c.isdigit() for c in text) and 
                (any(prefix in upper_text for prefix in ["INV", "PO", "REF", "IV"]) or
                 len(text) >= 6))
    
    def _has_continuation_marker(self, text: str) -> bool:
        markers = ["&", ",", "-", "...", "..", ";", ":", "\\", "/", "+", "cont", "continued", "(cont)"]
        return any(text.endswith(marker) for marker in markers)
    
    def _merge_continuation_text(self, current: str, continuation: str) -> str:
        if current.endswith("&"):
            return current[:-1] + " " + continuation
        elif current.endswith(",") or current.endswith("-"):
            return current + continuation
        elif current.endswith("...") or current.endswith(".."):
            return current.rstrip(".") + " " + continuation
        elif current.endswith(";") or current.endswith(":"):
            return current + " " + continuation
        elif current.endswith("\\") or current.endswith("/") or current.endswith("+"):
            return current[:-1] + " " + continuation
        elif any(current.endswith(marker) for marker in ["cont", "continued", "(cont)"]):
            for marker in ["cont", "continued", "(cont)"]:
                if current.endswith(marker):
                    return current[:-len(marker)].strip() + " " + continuation
        
        return current + " " + continuation