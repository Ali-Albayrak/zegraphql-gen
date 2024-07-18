import strawberry
from strawberry.permission import PermissionExtension
from business.types import DocumentType
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
        db = info.context.db
        obj = DocumentModel.objects(db)
        result = await obj.get(id=id)
        return result

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-list",
        "cybernetic-karari-documents-root-list",
        "cybernetic-karari-documents-tenant-list",
    ])
    ])])
    async def list_documents(self, info: strawberry.Info[GraphQLContext]) -> list[DocumentType]:
        db = info.context.db
        obj = DocumentModel.objects(db)
        result = await obj.all()
        return result
    