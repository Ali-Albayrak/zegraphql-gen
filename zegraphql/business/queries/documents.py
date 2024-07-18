import strawberry
from strawberry.permission import PermissionExtension
from graphql_types import DocumentType
from business.db_models.documents_model import DocumentModel
from core.depends import GraphQLContext
from core.auth import Protect





@strawberry.type
class DocumentQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-list",
        "cybernetic-karari-documents-root-list",
        "cybernetic-karari-documents-tenant-list",
    ])
    ])])
    async def get_document(self, id: strawberry.ID,  info: strawberry.Info[GraphQLContext]) -> DocumentType:
        # db = next(get_sync_db())
        # print(f"{info.context=}")
        # print(f"{dir(info.context)=}")
        # print(f"{type(info.context)=}")
        # print(f"{info.context.keys()=}")
        # print(f"{info.context['request']=}")
        # print(f"{dir(info.context['request'])=}")
        # print(f"{type(info.context['request'])=}")
        # print(f"{info.context.keys()=}")
        db = info.context.db
        obj = await DocumentModel.objects(db)
        result = await obj.get(id=id)
        return result

        if result:
            return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-list",
        "cybernetic-karari-documents-root-list",
        "cybernetic-karari-documents-tenant-list",
    ])
    ])])
    async def list_documents(self, info: strawberry.Info[GraphQLContext]) -> list[DocumentType]:
        db = info.context.db
        obj = await DocumentModel.objects(db)
        result = await obj.all()
        return result
    