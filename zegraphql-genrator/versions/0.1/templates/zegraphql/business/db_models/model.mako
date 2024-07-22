import os
import enum

<%!
    def get_column_dependencies(fields):
        depends = {'Column'}
        for field in fields:
            if 'text' == field['field_type']:
                depends.add('Text')
            if 'boolean' == field['field_type']:
                depends.add('BOOLEAN')
            if 'integer' == field['field_type']:
                depends.add('Integer')
            if 'lookup' == field['field_type']:
                depends.add('VARCHAR')
            if 'array' == field['field_type']:
                depends.add('ARRAY')
            if 'json' == field['field_type']:
                depends.add('JSON')
            if 'date' == field['field_type']:
                depends.add('DATE')
            if 'email' == field['field_type']:
                depends.add('Text')
            if 'select' == field['field_type']:
                if field.get("options") and field.get("options", {}).get("multi"):
                    depends.add('ARRAY')
                    depends.add(f'{get_column_dependencies([{"field_type": field.get("options", {}).get("type", "text")}]).split(", ")[-1]}')
                else:
                    depends.add('Enum')
            if 'rel' == field['field_type']:
                depends.add('String, ForeignKey')
        return ', '.join(list(depends))
%>\
from fastapi import HTTPException
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import ${get_column_dependencies(fields)}
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from core.base_model import BaseModel
from core.manager import Manager
from core.logger import log
from core.custom_exceptions import TriggerException

<%
def load_actions(triggers):
        if not triggers:
            return ""
        actions = ""
        triggers = triggers.values() or []
        for _triggers in triggers:
            for trigger in _triggers:
                if actions:
                    actions += ", " + trigger
                else:
                    actions += trigger
        return f"from actions import {actions}"
%>
${load_actions(triggers)}

% for field in fields:
% if field["field_type"] == "select" and field.get('options', {}).get("options", {}):
class ${get_pascal_case_without_underscore(field["name"])}Enum(${enum_field_type({"field_type": field.get('options', {}).get("type", "text")})}, enum.Enum):
    % for field_name in field.get('options', {}).get("options", []):
    ${field_name} = "${field_name}"
    % endfor
% endif
% endfor


<%!
    def trans_field_type(field):
        field_type = field['field_type']
        required = field.get('required')
        default = field.get('default')
        response = ''
        if field_type == 'integer':
            response = 'Integer'
        elif field_type == 'text':
            response = 'Text'
        elif field_type == 'boolean':
            response = 'BOOLEAN'
        elif field_type == 'select':
            if field.get("options") and field.get("options", {}).get("multi"):
                response = f'ARRAY({trans_field_type({"field_type": field.get("options", {}).get("type", "text")}).split(",")[0]})'
            else:
                response = f'Enum({field["name"].replace("_", " ").replace("-", " ").title().replace(" ", "")}Enum)'
        elif field_type == 'json':
            response = 'JSON'
        elif field_type == 'date':
            response = 'DATE'
        elif field_type == 'lookup':
            longest = max(field['options']['lookup_options'], key=len)
            response = f"VARCHAR({len(longest)})"
        elif field_type in ['image', 'file']:
            response = 'Text'
        elif field_type == 'email':
            response = 'Text'
        elif field_type == 'array':
            response = 'ARRAY(' + trans_field_type({"field_type": field['options']['array_of']}).split(',')[0] + ')'
        elif field_type == 'rel':
            response = 'Text'
        else:
            return "Unknown"
        if required:
            response += ", nullable=False"
        else:
            response += ", nullable=True"
        if default is None and field_type == 'boolean':
            response += f", default=False"
        elif default is not None:
            response += f", default={default}" if field_type in ["integer", "boolean"] else f", default='{default}'"
        else:
            response += f", default=None"
        return response
%>\
## get field annotations
        ## for field in fields:
        ##     field_name = field['name']
        ##     field_type = field['field_type']
        ##     required = field.get('required')
        ##     default = field.get('default')
        ##     if field_type == 'text':
        ##         annotations[field_name] = 'str'
        ##     elif field_type == 'integer':
        ##         annotations[field_name] = 'int'
        ##     elif field_type == 'boolean':
        ##         annotations[field_name] = 'bool'
        ##     elif field_type == 'select':
        ##         if field.get("options") and field.get("options", {}).get("multi"):
        ##             annotations[field_name] = f'List[{get_field_annotations([{"field_type": field.get("options", {}).get("type", "text")}])[field_name]}]'
        ##         else:
        ##             annotations[field_name] = f'{get_pascal_case_without_underscore(field_name)}Enum'
        ##     elif field_type == 'json':
        ##         annotations[field_name] = 'dict'
        ##     elif field_type == 'date':
        ##         annotations[field_name] = 'datetime.date'
        ##     elif field_type == 'lookup':
        ##         annotations[field_name] = 'str'
        ##     elif field_type in ['image', 'file']:
        ##         annotations[field_name] = 'uuid.UUID'
        ##     elif field_type == 'email':
        ##         annotations[field_name] = 'str'
        ##     elif field_type == 'array':
        ##         annotations[field_name] = f'List[{get_field_annotations([{"field_type": field['options']['array_of']}])[field_name]}]'
        ##     elif field_type == 'rel':
        ##         annotations[field_name] = 'uuid.UUID'
        ## return annotations
<%!
    def get_field_annotation(field):
        response = ''
        field_name = field['name']
        field_type = field['field_type']
        required = field.get('required')
        default = field.get('default')
        if field_type == 'text':
            response = 'str'
        elif field_type == 'integer':
            response = 'int'
        elif field_type == 'boolean':
            response = 'bool'
        elif field_type == 'select':
            if field.get("options") and field.get("options", {}).get("multi"):
                response = f'List[{get_field_annotation({"field_type": field.get("options", {}).get("type", "text")})}]'
            else:
                response = f'{get_pascal_case_without_underscore(field_name)}Enum'
        elif field_type == 'json':
            response = 'dict'
        elif field_type == 'date':
            response = 'datetime.date'
        elif field_type == 'lookup':
            response = 'str'
        elif field_type in ['image', 'file']:
            response = 'uuid.UUID'
        elif field_type == 'email':
            response = 'str'
        elif field_type == 'array':
            response = f'List[{get_field_annotation({"field_type": field['options']['array_of']})}]'
        elif field_type == 'rel':
            response = 'uuid.UUID'
        return response
%>\

class ${name.title()}Model(BaseModel):
    __tablename__ = '${plural}'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    % for field in fields:
        % if field['field_type'] in ['image', 'file'] :
            <% field_name = field['name'] %>
            ${field['name']}: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.files.id"))
            <% continue %>
        % endif
    % if field['field_type'] == 'rel':
        % if field['options'].get('parent'):
            <% parent_name = field['options']['parent'].replace('$', '') %>
        % if '$' in field['options'].get('parent', ''):
            <% parent = {"plural": parent_name} %>
            ${field['name']} = mapped_column(UUID(as_uuid=True), ForeignKey("zekoder_zeauth.${parent['plural']}s.id"))
            <% continue %>
        % endif
        <% parent = validate_relation(_fields, parent_name) %>
        ${field['name']} = mapped_column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".${parent['plural']}.id"))
        % if "__" in plural:   
            ${field['name']}__details = relationship("${parent["name"].title()}Model", foreign_keys=[${field['name']}], back_populates='${plural}')
        % else:
            ${field['name']}__details = relationship("${parent["name"].title()}Model", foreign_keys=[${field['name']}], back_populates='${field['name']}')
        % endif
        <% continue %>
        % elif field['options'].get('children'):
            % if '$' in field['options'].get('children', ''):
                <% child_name = field['options']['children'].replace('$', '') %>
                <% continue %>
            % endif
            <% child_name = field['options']['children'] %> <% child = validate_relation(_fields, child_name) %>
            % if is_peer_back_populate(child, plural):
                ${validate_relation(_fields, field['options']['children'])['plural']} = relationship('${child["name"].title()}Model', back_populates='${plural}__details')
            % else:
                from business.${child["plural"]}_model import ${child["name"].title()}Model
                ${field['name']} = relationship('${child["name"].title()}Model', foreign_keys=[${child["name"].title()}Model.${field['name']}], back_populates='${field['name']}__details')
            % endif
        % endif
        <% continue %>
    % endif
            <%%>
    ${field['name']}: Mapped[get_field_annotation(field)] = mapped_column(trans_field_type(field))
    % endfor

    @classmethod
    def objects(cls, session):
        % if triggers:
            return CustomManager(cls, session)
        % else:
            return Manager(cls, session)
        % endif