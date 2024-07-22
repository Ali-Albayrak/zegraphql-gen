import datetime
from typing import Optional, List
import strawberry
import enum

<%
# Helper function to generate fields for strawberry.type or strawberry.input classes
def generate_fields(fields):
    result = []
    for field in fields:
        field_name = field['name']
        field_type = field['field_type']
        optional = not field.get('required', False)
        options = field.get('options', {})
        
        if field_type == 'text':
            field_type_str = 'str'
        elif field_type == 'date':
            field_type_str = 'datetime.date'
        elif field_type == 'rel':
            field_type_str = f'"{options.get("parent", "str")}"'
        elif field_type == 'file':
            field_type_str = 'strawberry.ID'
        elif field_type == 'select':
            enum_name = f"{get_pascal_case_without_underscore(field_name)}Enum"
            field_type_str = enum_name
        else:
            field_type_str = 'str'
        
        if optional:
            field_type_str = f"Optional[{field_type_str}]"
        
        result.append(f"{field_name}: {field_type_str}")
    return '\n    '.join(result)
%>

class BaseType:
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_") and not callable(v)}

% for obj_name, obj_details in objects.items():
% for field in obj_details['fields']:
% if field['field_type'] == 'select':
<%
enum_name = f"{get_pascal_case_without_underscore(field['name'])}Enum"
options = field['options']['options']
%>
@strawberry.enum
class ${enum_name}(str, enum.Enum):
    % for option in options:
    ${option} = "${option}"
    % endfor
% endif
% endfor

@strawberry.type
class ${get_pascal_case_without_underscore(obj_name)}Type(BaseType):
    ${generate_fields(obj_details['fields'])}

@strawberry.input
class Create${get_pascal_case_without_underscore(obj_name)}Input(BaseType):
    ${generate_fields(obj_details['fields'])}

@strawberry.input
class Update${get_pascal_case_without_underscore(obj_name)}Input(BaseType):
    id: Optional[strawberry.ID] = None
    ${generate_fields(obj_details['fields'])}
% endfor
