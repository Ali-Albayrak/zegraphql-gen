import strawberry
from strawberry.permission import PermissionExtension
from business.types import IndustryType
from business.db_models.industries_model import IndustryModel
from core.depends import GraphQLContext
from core.auth import Protect





@strawberry.type
class IndustryQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-industries-list",
        "cybernetic-karari-industries-root-list",
        "cybernetic-karari-industries-tenant-list",
    ])
    ])])
    async def get_industry(self, id: strawberry.ID,  info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        obj = IndustryModel.objects(db)
        result = await obj.get(id=id)
        return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-industries-list",
        "cybernetic-karari-industries-root-list",
        "cybernetic-karari-industries-tenant-list",
    ])
    ])])
    async def list_industries(self, info: strawberry.Info[GraphQLContext]) -> list[IndustryType]:
        db = info.context.db
        obj = IndustryModel.objects(db)
        result = await obj.all()
        return result
    