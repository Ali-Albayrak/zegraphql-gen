import strawberry
from strawberry.permission import PermissionExtension
from business.types import ${get_pascal_case_without_underscore(name)}Type, Create${get_pascal_case_without_underscore(name)}Input, Update${get_pascal_case_without_underscore(name)}Input
from business.db_models.${plural}_model import ${get_pascal_case_without_underscore(name)}Model, ${get_pascal_case_without_underscore(plural)}Access
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class ${get_pascal_case_without_underscore(name)}Mutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.create_roles()
    ])])])
    async def create_${name}(self, input: Create${get_pascal_case_without_underscore(name)}Input, info: strawberry.Info[GraphQLContext]) -> ${get_pascal_case_without_underscore(name)}Type:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(name)}Model.objects(db)
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
        new_${name} = await obj.create(**kwargs)
        return new_${name}

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.update_roles()
    ])])])
    async def update_${name}(self, id: strawberry.ID, input: Update${get_pascal_case_without_underscore(name)}Input, info: strawberry.Info[GraphQLContext]) -> ${get_pascal_case_without_underscore(name)}Type:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(name)}Model.objects(db)
        result = await obj.update(id, **input.to_dict())
        return result

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        ## ${generate_permission(provider_name, app_name, obj_details['plural'], 'delete')}
        ${get_pascal_case_without_underscore(plural)}Access.delete_roles()
    ])])])
    async def delete_${name}(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(name)}Model.objects(db)
        result = await obj.delete(id)

        return True
<% endfor %>
