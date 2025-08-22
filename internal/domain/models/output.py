from dataclasses import dataclass
from typing import Optional, List, Dict
import json


@dataclass
class DocumentHeader:
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    statement_number: Optional[str] = None
    statement_date: Optional[str] = None
    base_currency: Optional[str] = None
    statement_total_balance: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    remit_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "supplier_name": self.supplier_name,
            "customer_name": self.customer_name,
            "customer_id": self.customer_id,
            "statement_number": self.statement_number,
            "statement_date": self.statement_date,
            "base_currency": self.base_currency,
            "statement_total_balance": self.statement_total_balance,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "remit_to": self.remit_to
        }


@dataclass
class OrderedFieldMap:
    keys: List[str]
    values: Dict[str, Optional[str]]
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        result = {}
        for key in self.keys:
            result[key] = self.values.get(key)
        return result


@dataclass
class ExtractionResult:
    header: DocumentHeader
    lines: List[OrderedFieldMap]
    
    def to_dict(self) -> Dict:
        return {
            "header": self.header.to_dict(),
            "lines": [line.to_dict() for line in self.lines]
        }