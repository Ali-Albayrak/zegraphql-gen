import strawberry
from strawberry.permission import PermissionExtension
from graphql_types import IndustryType, CreateIndustryInput, UpdateIndustryInput
from business.db_models.industries_model import IndustryModel
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class IndustryMutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-industries-create",
    ])
    ])])
    async def create_industry(self, input: CreateIndustryInput, info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        log.debug(f"{input=}")
        log.debug(f"{dir(input)=}")
        obj = IndustryModel.objects(db)
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
        new_industry = await obj.create(**kwargs)
        return new_industry
    
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-industries-update",
        ]
        )])
    ])
    async def update_industry(self, id: strawberry.ID, input: UpdateIndustryInput, info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        obj = IndustryModel.objects(db)
        result = await obj.update(id, **input.to_dict())
        return result
    
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-industries-delete",
        ]
        )])
    ])
    async def delete_industry(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        obj = IndustryModel.objects(db)
        result = await obj.delete(id)
        
        return True