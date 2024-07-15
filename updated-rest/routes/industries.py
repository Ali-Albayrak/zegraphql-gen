

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

from business.industries_schema import *
from business.industries_model import IndustryModel


router = APIRouter()


# list industries
@router.get('/', tags=['industries'], status_code=HTTP_200_OK, summary="List industries", response_model=ReadIndustries)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_sync_db), commons: CommonDependencies = Depends(CommonDependencies)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.list_roles())
    try:
        obj = await IndustryModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of industries")

list.__doc__ = f" List industries".expandtabs()


# get industry
@router.get('/industry_id', tags=['industries'], status_code=HTTP_200_OK, summary="Get industry with ID", response_model=ReadIndustry)
async def get(request: Request, industry_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.list_roles())
    try:
        obj = await IndustryModel.objects(db)
        result = await obj.get(id=industry_id)

        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(404, f"<{industry_id}> record not found in industries")
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"could not fetch record <{industry_id}>")

get.__doc__ = f" Get a specific industry by its id".expandtabs()


# query industries
@router.post('/q', tags=['industries'], status_code=HTTP_200_OK, deprecated=True, summary="Query industries: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(request: Request, q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.list_roles())

    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, IndustryModel)
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



# create industry
@router.post('/', tags=['industries'], status_code=HTTP_201_CREATED, summary="Create new industry", response_model=ReadIndustry)
async def create(request: Request, industry: CreateIndustry, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.create_roles())

    try:
        obj = await IndustryModel.objects(db)
        new_data = industry.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_industry = await obj.create(**kwargs)
        return new_industry
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new industry failed")

create.__doc__ = f" Create a new industry".expandtabs()


# create multiple industries
@router.post('/add-industries', tags=['industries'], status_code=HTTP_201_CREATED, summary="Create multiple industries", response_model=List[ReadIndustry])
async def create_multiple_industries(request: Request, industries: List[CreateIndustry], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.create_roles())

    new_items, errors_info = [], []
    try:
        for industry_index, industry in enumerate(industries):
            try:
                obj = await IndustryModel.objects(db)
                new_data = industry.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_industries = await obj.create(only_add=True, **kwargs)
                new_items.append(new_industries)
            except HTTPException as e:
                errors_info.append({"index": industry_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new industries failed")

create.__doc__ = f" Create multiple new industries".expandtabs()


# upsert multiple industries
@router.post('/upsert-multiple-industries', tags=['industries'], status_code=HTTP_201_CREATED, summary="Upsert multiple industries", response_model=List[ReadIndustry])
async def upsert_multiple_industries(request: Request, industries: List[CreateIndustry], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.create_roles() + IndustriesAccess.update_roles())
    new_items, errors_info = [], []
    try:
        for industry_index, industry in enumerate(industries):
            try:
                obj = await IndustryModel.objects(db)
                new_data = industry.dict()
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
                    obj = await IndustryModel.objects(db)
                    await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(data)
                else:
                    new_industries = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_industries)
            except HTTPException as e:
                errors_info.append({"index": industry_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple industries failed")

upsert_multiple_industries.__doc__ = f" upsert multiple industries".expandtabs()


# update industry
@router.put('/industry_id', tags=['industries'], status_code=HTTP_201_CREATED, summary="Update industry with ID", response_model=ReadIndustry)
async def update(request: Request, industry_id: UUID, industry: UpdateIndustry, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.update_roles())

    try:
        obj = await IndustryModel.objects(db)
        data = await obj.get(id=industry_id)
        if not data:
            raise FileNotFoundError
        new_data = industry.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": data.to_dict() if data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        await obj.update(obj_id=industry_id, **kwargs)
        return data
    except FileNotFoundError:
        raise HTTPException(404, f"<{industry_id}> record not found in industries")
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed updating record with id <{industry_id}> in industries")

update.__doc__ = f" Update a industry by its id and payload".expandtabs()


# delete industry
@router.delete('/industry_id', tags=['industries'], status_code=HTTP_204_NO_CONTENT, summary="Delete industry with ID", response_class=Response)
async def delete(request: Request, industry_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.delete_roles())
    try:
        obj = await IndustryModel.objects(db)
        old_data = await obj.get(id=industry_id)
        if not old_data:
            return JSONResponse(content={"message": f"<{industry_id}> record not found in industries"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await IndustryModel.objects(db)
        await obj.delete(obj_id=industry_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a industry by its id".expandtabs()


# delete multiple industries
@router.delete('/delete-industries', tags=['industries'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple industries with IDs", response_class=Response)
async def delete_multiple_industries(request: Request, industries_id: List[str] = QueryParam(), db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(IndustriesAccess.delete_roles())
    try:
        obj = await IndustryModel.objects(db)
        all_old_data = await obj.get_multiple(obj_ids=industries_id)

        if not all_old_data:
            return JSONResponse(content={"message": f"<{industries_id}> record not found in industries"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": all_old_data if len(all_old_data) > 0 else [],
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await IndustryModel.objects(db)
        await obj.delete_multiple(obj_ids=industries_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed deleting industries_id <{industries_id}>")

delete.__doc__ = f" Delete multiple industries by list of ids".expandtabs()