import os
import enum
import uuid
import datetime
% if 'rel' in [field['field_type'] for field in fields]:
import importlib
% endif

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
<%!
    def enum_field_type(field_type):
        if field_type == 'integer':
            return 'int'
        elif field_type == 'decimal':
            return 'float'
        return 'str'
%>\
from fastapi import HTTPException
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import ${get_column_dependencies(fields)}
from sqlalchemy.orm import relationship, Mapped, mapped_column
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

% if triggers:
class CustomManager(Manager):
    % if triggers and triggers.get("create"):
    async def pre_create(self, **kwargs) -> dict:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("create"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="create")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in pre_create trigger has been skipped")
            log.debug(err)
            log.error("Error while executing pre_create trigger, check the debug above!")
            return new_data
    % endif

    % if triggers and triggers.get("post_create"):
    async def post_create(self, **kwargs) -> dict:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("post_create"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="create")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in post_create trigger has been skipped")
            log.debug(err)
            log.error("Error while executing post_create trigger, check the debug above!")
            return new_data
    % endif

    % if triggers and triggers.get("update"):
    async def pre_update(self, **kwargs) -> dict:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("update"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="update")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in pre_update trigger has been skipped")
            log.debug(err)
            log.error("Error while executing pre_update trigger, check the debug above!")
            return new_data
    % endif

    % if triggers and triggers.get("post_update"):
    async def post_update(self, **kwargs) -> dict:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("post_update"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="update")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in post_update trigger has been skipped")
            log.debug(err)
            log.error("Error while executing post_update trigger, check the debug above!")
            return new_data
    % endif

    % if triggers and triggers.get("delete"):
    async def pre_delete(self, **kwargs) -> bool:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("delete"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="delete")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in pre_delete trigger has been skipped")
            log.debug(err)
            log.error("Error while executing pre_delete trigger, check the debug above!")
            return new_data
    % endif

    % if triggers and triggers.get("post_delete"):
    async def post_delete(self, **kwargs) -> bool:
        try:
            jwt = kwargs.get("jwt", {})
            new_data = kwargs.get("new_data", {})
            old_data = kwargs.get("old_data", {})
            well_known_urls = kwargs.get("well_known_urls", {})
            % for trigger in triggers.get("post_delete"):
            new_data = ${trigger}.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="delete")
            % endfor
            return new_data
        except TriggerException as e:
            raise e
        except Exception as err:
            log.warn("at least one step in post_delete trigger has been skipped")
            log.debug(err)
            log.error("Error while executing post_delete trigger, check the debug above!")
            return new_data
    % endif
% endif

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

<%!
    def get_field_annotation(field):
        response = ''
        field_name = field.get('name')
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
                response = f'list[{get_field_annotation({"field_type": field.get("options", {}).get("type", "text")})}]'
            else:
                response = f'{field["name"].replace("_", " ").replace("-", " ").title().replace(" ", "")}Enum'
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
            response = f'list[{get_field_annotation({"field_type": field["options"]["array_of"]})}]'
        elif field_type == 'rel':
            response = 'uuid.UUID'
        return response
%>\
<%!
    def validate_relation(_fields, relation):
        plural = None
        for key, value in _fields.data.items():
            if value["plural"] == relation:
                value["name"] = key
                plural = value
        return plural
%>
<%!
    def is_peer_back_populate(child, plural):
        for value in child.get("fields"):
            if value["name"] == plural:
                return plural
        return
%>


class ${get_pascal_case_without_underscore(name)}Model(BaseModel):
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
    ${field['name']}__details = relationship("${parent["name"].title()}Model", foreign_keys=[${field['name']}], back_populates='${plural}', lazy='selectin')
    % else:
    ${field['name']}__details = relationship("${parent["name"].title()}Model", foreign_keys=[${field['name']}], back_populates='${field['name']}', lazy='selectin')
    % endif
<% continue %>
    % elif field['options'].get('children'):
    % if '$' in field['options'].get('children', ''):
    <% child_name = field['options']['children'].replace('$', '') %>
<% continue %>
    % endif
    <% child_name = field['options']['children'] %> <% child = validate_relation(_fields, child_name) %>
    % if is_peer_back_populate(child, plural):
    ${validate_relation(_fields, field['options']['children'])['plural']} = relationship('${child["name"].title()}Model', back_populates='${plural}__details', lazy='selectin')
    % else:
    from business.db_models.${child["plural"]}_model import ${child["name"].title()}Model
    ${field['name']} = relationship('${child["name"].title()}Model', foreign_keys=[${child["name"].title()}Model.${field['name']}], back_populates='${field['name']}__details', lazy='selectin')
    % endif
    % endif
<% continue %>
    % endif
    ${field['name']}: Mapped[${get_field_annotation(field)}] = mapped_column(${trans_field_type(field)})
    % endfor

    @classmethod
    def objects(cls, session):
        % if triggers:
        return CustomManager(cls, session)
        % else:
        return Manager(cls, session)
        % endif




<%
    def get_related_tables():
        """
        To have full access on a table user must have proper proper roles on tables which attached to this table to fetch the details properly 
        """
        related_tables = [plural]
        for field in fields:
            if field['field_type'] == 'rel':
                if parent := field['options'].get('parent'):
                    if '$' not in parent:
                        related_tables.append(parent)
                if children := field['options'].get('children'):
                    related_tables.append(children)
        return related_tables

    def generate_related_roles():
        related_tables = get_related_tables()
        related_roles = []
        for table in related_tables:
            role_prefix = f"{app_provider}-{app_name}-{table}"
            related_roles.extend([
                f"{role_prefix}-list",
                f"{role_prefix}-tenant-list",
                f"{role_prefix}-root-list"
            ])
        return related_roles

    def generate_target_table_roles(action:str) -> str:
        """
        Add protection layer in the begining of the method if solution is secured.

        Parameters:
        - action (str): The action for which roles are generated.
        """
        current_table = plural

        role_prefix = f"{app_provider}-{app_name}-{current_table}"
        current_table_roles = [
            f"{role_prefix}-{action}",
            f"{role_prefix}-tenant-{action}",
            f"{role_prefix}-root-{action}"
        ]
        return current_table_roles

%>\

class ${get_pascal_case_without_underscore(plural)}Access:
    related_access_roles = ${generate_related_roles()}     

    @classmethod
    def list_roles(cls):
        list_roles = ${generate_target_table_roles('list')}
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ${generate_target_table_roles('create')}
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ${generate_target_table_roles('update')}
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ${generate_target_table_roles('delete')}
        return delete_roles + cls.related_access_roles
