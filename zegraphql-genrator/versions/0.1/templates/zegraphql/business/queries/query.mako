import strawberry
from strawberry.permission import PermissionExtension
from business.types import ${get_pascal_case_without_underscore(name)}Type
from business.db_models.${plural}_model import ${get_pascal_case_without_underscore(name)}Model, ${get_pascal_case_without_underscore(plural)}Access
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class ${get_pascal_case_without_underscore(name)}Query:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.list_roles()
    ])])])
    async def get_${name}(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> ${get_pascal_case_without_underscore(name)}Type:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(name)}Model.objects(db)
        result = await obj.get(id=id)
        return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        ${get_pascal_case_without_underscore(plural)}Access.list_roles()
    ])])])
    async def list_${plural}(self, info: strawberry.Info[GraphQLContext]) -> list[${get_pascal_case_without_underscore(name)}Type]:
        db = info.context.db
        obj = ${get_pascal_case_without_underscore(name)}Model.objects(db)
        result = await obj.all()
        return result
