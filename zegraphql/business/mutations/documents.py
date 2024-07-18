import strawberry
from strawberry.permission import PermissionExtension
from graphql_types import DocumentType, CreateDocumentInput, UpdateDocumentInput
from business.db_models.documents_model import DocumentModel
from core.depends import GraphQLContext
from core.auth import Protect

@strawberry.type
class DocumentMutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-create",
    ])
    ])])
    async def create_document(self, input: CreateDocumentInput, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        obj = DocumentModel.objects(db)
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
        new_document = await obj.create(**kwargs)
        return new_document

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-update",
    ])
    ])])
    async def update_document(self, id: strawberry.ID, input: UpdateDocumentInput, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        obj = DocumentModel.objects(db)
        result = await obj.update(id, **input.to_dict())
        return result

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect([
        "cybernetic-karari-documents-delete",
    ])
    ])])
    async def delete_document(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        obj = DocumentModel.objects(db)
        result = await obj.delete(id)

        return True