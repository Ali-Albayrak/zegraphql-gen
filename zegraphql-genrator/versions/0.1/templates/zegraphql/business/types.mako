import datetime
from typing import Optional, List
import strawberry
import enum

<%!
    def get_relation(_fields, relation):
        for key, value in _fields.data.items():
            if value["plural"] == relation:
                return key
        return None
%>

<%
# Helper function to generate fields for strawberry.type or strawberry.input classes
def generate_fields(obj_name, fields, schema_type='type'):
    result = []
    for field in fields:
        field_name = field['name']
        field_type = field['field_type']
        optional = not field.get('required', False)
        options = field.get('options', {})
        field_type_str = ''

        if optional:
            field_type_str = "Optional[{0}] = None"
        else:
            field_type_str = "{0}"

        if field_type == 'text':
            field_type_str = field_type_str.format('str')
        elif field_type == 'date':
            field_type_str = field_type_str.format('datetime.date')
        elif field_type == 'rel':
            if schema_type == 'type':
                if options.get("parent"):
                    result.append(f"{field_name}: {field_type_str.format('strawberry.ID')}")
                    relation = get_relation(objects, options.get("parent"))
                    field_name = f"{field_name}__details"
                    rel_type = f'"{get_pascal_case_without_underscore(relation)}Type"'
                    field_type_str = field_type_str.format(rel_type)
                elif options.get("children"):
                    relation = get_relation(objects, options.get("children"))
                    rel_type = f'list["{get_pascal_case_without_underscore(relation)}Type"]'
                    field_type_str = field_type_str.format(rel_type)
                else:
                    field_type_str = field_type_str.format('strawberry.JSON')
                result.append(f"{field_name}: {field_type_str}")
            continue
        elif field_type == 'file':
            field_type_str = field_type_str.format('strawberry.ID')
        elif field_type == 'select':
            enum_name = f"{get_pascal_case_without_underscore(obj_name)}{get_pascal_case_without_underscore(field_name)}Enum"
            field_type_str = field_type_str.format(enum_name)
        else:
            field_type_str = field_type_str.format('str')

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
enum_name = f"{get_pascal_case_without_underscore(obj_name)}{get_pascal_case_without_underscore(field['name'])}Enum"
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
    id: Optional[strawberry.ID] = None
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[strawberry.ID] = None
    updated_by: Optional[strawberry.ID] = None
    tenant_id: Optional[strawberry.ID]  = None
    ${generate_fields(obj_name ,obj_details['fields'], 'type')}

@strawberry.input
class Create${get_pascal_case_without_underscore(obj_name)}Input(BaseType):
    id: Optional[strawberry.ID] = None
    ${generate_fields(obj_name, obj_details['fields'], 'input')}

@strawberry.input
class Update${get_pascal_case_without_underscore(obj_name)}Input(BaseType):
    ${generate_fields(obj_name, obj_details['fields'], 'input')}
% endfor
