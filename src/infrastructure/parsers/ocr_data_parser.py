import re
from typing import List
from ...domain.interfaces.parser import OCRDataParser
from ...domain.models.document import OCRToken, BoundingBox


class OCRDataParserImpl(OCRDataParser):
    def __init__(self):
        self.ocr_line_pattern = re.compile(r'^(.*?)\s*\|\s*\[(.*?)\]\s*$')
    
    def parse_ocr_tokens(self, data: str) -> List[OCRToken]:
        tokens = []
        lines = data.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('###'):
                continue
            
            match = self.ocr_line_pattern.match(line)
            if not match:
                continue
            
            text = match.group(1).strip()
            coordinates_str = match.group(2)
            coordinates = [coord.strip() for coord in coordinates_str.split(',')]
            
            if len(coordinates) != 4:
                continue
            
            try:
                x0 = float(coordinates[0])
                y0 = float(coordinates[1])
                x1 = float(coordinates[2])
                y1 = float(coordinates[3])
                
                token = OCRToken(
                    text=text,
                    bounding_box=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1)
                )
                tokens.append(token)
            except ValueError:
                continue
        
        return tokens