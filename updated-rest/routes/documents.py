

from typing import Union, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED



from core.depends import CommonDependencies, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.documents_schema import *
from business.documents_model import DocumentModel


router = APIRouter()


# list documents
@router.get('/', tags=['documents'], status_code=HTTP_200_OK, summary="List documents", response_model=ReadDocuments)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_sync_db), commons: CommonDependencies = Depends(CommonDependencies)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.list_roles())
    try:
        obj = await DocumentModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of documents")

list.__doc__ = f" List documents".expandtabs()


# get document
@router.get('/document_id', tags=['documents'], status_code=HTTP_200_OK, summary="Get document with ID", response_model=ReadDocument)
async def get(request: Request, document_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.list_roles())
    try:
        obj = await DocumentModel.objects(db)
        result = await obj.get(id=document_id)

        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(404, f"<{document_id}> record not found in documents")
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"could not fetch record <{document_id}>")

get.__doc__ = f" Get a specific document by its id".expandtabs()


# query documents
@router.post('/q', tags=['documents'], status_code=HTTP_200_OK, deprecated=True, summary="Query documents: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(request: Request, q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.list_roles())

    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, DocumentModel)
        log.debug(q)
        allowed_aggregates = q.group
        result = jq.query(q, allowed_aggregates)
        return {
            'data': result.get("data", []),
            'aggregates': result.get("aggregates", []),
            'count': result.get("count", []),
            'page_size': size,
            'next_page': int(page) + 1
        }
    except UnkownOperator as e:
        log.debug(e)
        raise HTTPException(400, str(e))
    except ColumnNotFound as e:
        log.debug(e)
        raise HTTPException(400, str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of sessions due to unknown error")



# create document
@router.post('/', tags=['documents'], status_code=HTTP_201_CREATED, summary="Create new document", response_model=ReadDocument)
async def create(request: Request, document: CreateDocument, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.create_roles())

    try:
        obj = await DocumentModel.objects(db)
        new_data = document.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_document = await obj.create(**kwargs)
        return new_document
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new document failed")

create.__doc__ = f" Create a new document".expandtabs()


# create multiple documents
@router.post('/add-documents', tags=['documents'], status_code=HTTP_201_CREATED, summary="Create multiple documents", response_model=List[ReadDocument])
async def create_multiple_documents(request: Request, documents: List[CreateDocument], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.create_roles())

    new_items, errors_info = [], []
    try:
        for document_index, document in enumerate(documents):
            try:
                obj = await DocumentModel.objects(db)
                new_data = document.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_documents = await obj.create(only_add=True, **kwargs)
                new_items.append(new_documents)
            except HTTPException as e:
                errors_info.append({"index": document_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new documents failed")

create.__doc__ = f" Create multiple new documents".expandtabs()


# upsert multiple documents
@router.post('/upsert-multiple-documents', tags=['documents'], status_code=HTTP_201_CREATED, summary="Upsert multiple documents", response_model=List[ReadDocument])
async def upsert_multiple_documents(request: Request, documents: List[CreateDocument], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.create_roles() + DocumentsAccess.update_roles())
    new_items, errors_info = [], []
    try:
        for document_index, document in enumerate(documents):
            try:
                obj = await DocumentModel.objects(db)
                new_data = document.dict()
                data = await obj.get(id=new_data['id'])
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                if data:
                    kwargs['signal_data']['old_data'] = data.to_dict() if data else {}
                    obj = await DocumentModel.objects(db)
                    await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(data)
                else:
                    new_documents = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_documents)
            except HTTPException as e:
                errors_info.append({"index": document_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple documents failed")

upsert_multiple_documents.__doc__ = f" upsert multiple documents".expandtabs()


# update document
@router.put('/document_id', tags=['documents'], status_code=HTTP_201_CREATED, summary="Update document with ID", response_model=ReadDocument)
async def update(request: Request, document_id: UUID, document: UpdateDocument, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.update_roles())

    try:
        obj = await DocumentModel.objects(db)
        data = await obj.get(id=document_id)
        if not data:
            raise FileNotFoundError
        new_data = document.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": data.to_dict() if data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        await obj.update(obj_id=document_id, **kwargs)
        return data
    except FileNotFoundError:
        raise HTTPException(404, f"<{document_id}> record not found in documents")
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed updating record with id <{document_id}> in documents")

update.__doc__ = f" Update a document by its id and payload".expandtabs()


# delete document
@router.delete('/document_id', tags=['documents'], status_code=HTTP_204_NO_CONTENT, summary="Delete document with ID", response_class=Response)
async def delete(request: Request, document_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.delete_roles())
    try:
        obj = await DocumentModel.objects(db)
        old_data = await obj.get(id=document_id)
        if not old_data:
            return JSONResponse(content={"message": f"<{document_id}> record not found in documents"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await DocumentModel.objects(db)
        await obj.delete(obj_id=document_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a document by its id".expandtabs()


# delete multiple documents
@router.delete('/delete-documents', tags=['documents'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple documents with IDs", response_class=Response)
async def delete_multiple_documents(request: Request, documents_id: List[str] = QueryParam(), db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(DocumentsAccess.delete_roles())
    try:
        obj = await DocumentModel.objects(db)
        all_old_data = await obj.get_multiple(obj_ids=documents_id)

        if not all_old_data:
            return JSONResponse(content={"message": f"<{documents_id}> record not found in documents"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": all_old_data if len(all_old_data) > 0 else [],
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await DocumentModel.objects(db)
        await obj.delete_multiple(obj_ids=documents_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed deleting documents_id <{documents_id}>")

delete.__doc__ = f" Delete multiple documents by list of ids".expandtabs()