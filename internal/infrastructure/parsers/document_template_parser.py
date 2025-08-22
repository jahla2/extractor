import json
from ...domain.interfaces.parser import DocumentTemplateParser
from ...domain.models.document import DocumentTemplate, FieldSpecification, ColumnSpecification


class DocumentTemplateParserImpl(DocumentTemplateParser):
    def __init__(self):
        pass
    
    def parse_document_template(self, data: bytes) -> DocumentTemplate:
        template_data = json.loads(data.decode('utf-8'))
        
        # Parse header fields
        header = {}
        if 'header' in template_data and template_data['header'] is not None:
            for key, field_data in template_data['header'].items():
                if field_data is not None:
                    header[key] = FieldSpecification(
                        value=field_data.get('value'),
                        token_bboxes=field_data.get('token_bboxes'),
                        bbox=field_data.get('bbox')
                    )
        
        # Parse columns
        columns = []
        if 'columns' in template_data and template_data['columns'] is not None:
            for col_data in template_data['columns']:
                if col_data is not None:
                    columns.append(ColumnSpecification(
                        source=col_data['source'],
                        canonical=col_data['canonical'],
                        bbox=col_data['bbox'],
                        token_bboxes=col_data.get('token_bboxes')
                    ))
        
        return DocumentTemplate(header=header, columns=columns)