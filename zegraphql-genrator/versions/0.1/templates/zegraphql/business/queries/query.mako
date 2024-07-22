<%!
# Helper function to generate permission strings
def generate_permissions(provider_name, app_name, plural_name):
    return [
        f"{provider_name}-{app_name}-{plural_name}-list",
        f"{provider_name}-{app_name}-{plural_name}-root-list",
        f"{provider_name}-{app_name}-{plural_name}-tenant-list"
    ]
%>
## this for loop should be removed after figuring out how to get variables from the manifest file
## % for obj_name, obj_details in objects.items():
import strawberry
from strawberry.permission import PermissionExtension
from business.types import ${obj_name.capitalize()}Type
from business.db_models.${obj_name}_model import ${obj_name.capitalize()}Model
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class ${obj_name.capitalize()}Query:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        % for perm in generate_permissions(provider_name, app_name, obj_details['plural']):
        "${perm}",
        % endfor
    ])])])
    async def get_${obj_name}(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> ${obj_name.capitalize()}Type:
        db = info.context.db
        obj = ${obj_name.capitalize()}Model.objects(db)
        result = await obj.get(id=id)
        return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        % for perm in generate_permissions(provider_name, app_name, obj_details['plural']):
        "${perm}",
        % endfor
    ])])])
    async def list_${obj_details['plural']}(self, info: strawberry.Info[GraphQLContext]) -> list[${obj_name.capitalize()}Type]:
        db = info.context.db
        obj = ${obj_name.capitalize()}Model.objects(db)
        result = await obj.all()
        return result
