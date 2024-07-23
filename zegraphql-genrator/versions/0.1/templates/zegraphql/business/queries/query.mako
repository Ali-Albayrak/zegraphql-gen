<%!
    obj_name = name
    plural = plural
%>
## this for loop should be removed after figuring out how to get variables from the manifest file
## % for obj_name, obj_details in objects.items():
import strawberry
from strawberry.permission import PermissionExtension
from business.types import ${get_pascal_case_without_underscore(obj_name)}Type
from business.db_models.${plural}_model import ${get_pascal_case_without_underscore(obj_name)}Model, ${get_pascal_case_without_underscore(plural)}Access
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class ${get_pascal_case_without_underscore(obj_name)}Query:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.list_roles()
    ])])])
    async def get_${obj_name}(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> ${get_pascal_case_without_underscore(obj_name)}Type:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(obj_name)}Model.objects(db)
        result = await obj.get(id=id)
        return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.list_roles()
    ])])])
    async def list_${obj_details['plural']}(self, info: strawberry.Info[GraphQLContext]) -> list[${get_pascal_case_without_underscore(obj_name)}Type]:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(obj_name)}Model.objects(db)
        result = await obj.all()
        return result
