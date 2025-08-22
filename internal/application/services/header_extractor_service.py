from typing import Optional
from ...domain.interfaces.parser import HeaderExtractor, TokenMatcher
from ...domain.models.document import DocumentTemplate
from ...domain.models.output import DocumentHeader
from ...utils.token_utils import sort_tokens_by_x_with_tolerance, join_tokens_smartly, create_string_pointer


class HeaderExtractorService(HeaderExtractor):
    def __init__(self, template: DocumentTemplate, token_matcher: TokenMatcher, row_tolerance: float):
        self.template = template
        self.token_matcher = token_matcher
        self.row_tolerance = row_tolerance
    
    def extract_header(self) -> DocumentHeader:
        def extract_field_value(field_key: str) -> Optional[str]:
            if field_key not in self.template.header:
                return None
            
            specification = self.template.header[field_key]
            
            if specification.value and specification.value.strip():
                return create_string_pointer(specification.value.strip())
            
            token_boxes = specification.get_token_bounding_boxes()
            if token_boxes:
                tokens = self.token_matcher.get_tokens_by_bounding_boxes(token_boxes)
                sort_tokens_by_x_with_tolerance(tokens, self.row_tolerance)
                text = join_tokens_smartly(tokens)
                return create_string_pointer(text)
            
            bounding_box, has_box = specification.get_bounding_box()
            if has_box and bounding_box:
                tokens = self.token_matcher.get_tokens_in_bounding_box(bounding_box)
                sort_tokens_by_x_with_tolerance(tokens, self.row_tolerance)
                text = join_tokens_smartly(tokens)
                return create_string_pointer(text)
            
            return None
        
        return DocumentHeader(
            supplier_name=extract_field_value("supplier_name"),
            customer_name=extract_field_value("customer_name"),
            customer_id=extract_field_value("customer_id"),
            statement_number=extract_field_value("statement_number"),
            statement_date=extract_field_value("statement_date"),
            base_currency=extract_field_value("base_currency"),
            statement_total_balance=extract_field_value("statement_total_balance"),
            period_start=extract_field_value("period_start"),
            period_end=extract_field_value("period_end"),
            remit_to=extract_field_value("remit_to")
        )