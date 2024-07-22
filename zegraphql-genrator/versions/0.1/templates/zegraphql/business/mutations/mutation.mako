<%!
# Helper function to generate permission strings for mutations
def generate_permission(provider_name, app_name, plural_name, permission_type):
    permissions = [
        f"{provider_name}-{app_name}-{plural_name}-{permission_type}"
    ]
    if permission_type != 'create':
        permissions.append(f"{provider_name}-{app_name}-{plural_name}-tenant-{permission_type}")
        permissions.append(f"{provider_name}-{app_name}-{plural_name}-root-{permission_type}")
    return permissions
%>

## <% for obj_name, obj_details in objects.items(): %>
import strawberry
from strawberry.permission import PermissionExtension
from business.types import ${obj_name.capitalize()}Type, Create${obj_name.capitalize()}Input, Update${obj_name.capitalize()}Input
from business.db_models.${obj_name}_model import ${obj_name.capitalize()}Model
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class ${obj_name.capitalize()}Mutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ${generate_permission(provider_name, app_name, obj_details['plural'], 'create')}
    ])])])
    async def create_${obj_name}(self, input: Create${obj_name.capitalize()}Input, info: strawberry.Info[GraphQLContext]) -> ${obj_name.capitalize()}Type:
        db = info.context.db
        obj = ${obj_name.capitalize()}Model.objects(db)
        new_data = input.to_dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt":"",
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {}
            }
        }
        new_${obj_name} = await obj.create(**kwargs)
        return new_${obj_name}

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ${generate_permission(provider_name, app_name, obj_details['plural'], 'update')}
    ])])])
    async def update_${obj_name}(self, id: strawberry.ID, input: Update${obj_name.capitalize()}Input, info: strawberry.Info[GraphQLContext]) -> ${obj_name.capitalize()}Type:
        db = info.context.db
        obj = ${obj_name.capitalize()}Model.objects(db)
        result = await obj.update(id, **input.to_dict())
        return result

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ${generate_permission(provider_name, app_name, obj_details['plural'], 'delete')}
    ])])])
    async def delete_${obj_name}(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        obj = ${obj_name.capitalize()}Model.objects(db)
        result = await obj.delete(id)

        return True
<% endfor %>
