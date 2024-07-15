

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

from business.summary_tasks_schema import *
from business.summary_tasks_model import Summary_TaskModel


router = APIRouter()


# list summary_tasks
@router.get('/', tags=['summary_tasks'], status_code=HTTP_200_OK, summary="List summary_tasks", response_model=ReadSummary_Tasks)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_sync_db), commons: CommonDependencies = Depends(CommonDependencies)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.list_roles())
    try:
        obj = await Summary_TaskModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of summary_tasks")

list.__doc__ = f" List summary_tasks".expandtabs()


# get summary_task
@router.get('/summary_task_id', tags=['summary_tasks'], status_code=HTTP_200_OK, summary="Get summary_task with ID", response_model=ReadSummary_Task)
async def get(request: Request, summary_task_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.list_roles())
    try:
        obj = await Summary_TaskModel.objects(db)
        result = await obj.get(id=summary_task_id)

        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(404, f"<{summary_task_id}> record not found in summary_tasks")
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"could not fetch record <{summary_task_id}>")

get.__doc__ = f" Get a specific summary_task by its id".expandtabs()


# query summary_tasks
@router.post('/q', tags=['summary_tasks'], status_code=HTTP_200_OK, deprecated=True, summary="Query summary_tasks: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(request: Request, q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.list_roles())

    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, Summary_TaskModel)
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



# create summary_task
@router.post('/', tags=['summary_tasks'], status_code=HTTP_201_CREATED, summary="Create new summary_task", response_model=ReadSummary_Task)
async def create(request: Request, summary_task: CreateSummary_Task, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.create_roles())

    try:
        obj = await Summary_TaskModel.objects(db)
        new_data = summary_task.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_summary_task = await obj.create(**kwargs)
        return new_summary_task
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new summary task failed")

create.__doc__ = f" Create a new summary_task".expandtabs()


# create multiple summary_tasks
@router.post('/add-summary_tasks', tags=['summary_tasks'], status_code=HTTP_201_CREATED, summary="Create multiple summary_tasks", response_model=List[ReadSummary_Task])
async def create_multiple_summary_tasks(request: Request, summary_tasks: List[CreateSummary_Task], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.create_roles())

    new_items, errors_info = [], []
    try:
        for summary_task_index, summary_task in enumerate(summary_tasks):
            try:
                obj = await Summary_TaskModel.objects(db)
                new_data = summary_task.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_summary_tasks = await obj.create(only_add=True, **kwargs)
                new_items.append(new_summary_tasks)
            except HTTPException as e:
                errors_info.append({"index": summary_task_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new summary tasks failed")

create.__doc__ = f" Create multiple new summary_tasks".expandtabs()


# upsert multiple summary_tasks
@router.post('/upsert-multiple-summary_tasks', tags=['summary_tasks'], status_code=HTTP_201_CREATED, summary="Upsert multiple summary_tasks", response_model=List[ReadSummary_Task])
async def upsert_multiple_summary_tasks(request: Request, summary_tasks: List[CreateSummary_Task], db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.create_roles() + Summary_TasksAccess.update_roles())
    new_items, errors_info = [], []
    try:
        for summary_task_index, summary_task in enumerate(summary_tasks):
            try:
                obj = await Summary_TaskModel.objects(db)
                new_data = summary_task.dict()
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
                    obj = await Summary_TaskModel.objects(db)
                    await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(data)
                else:
                    new_summary_tasks = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_summary_tasks)
            except HTTPException as e:
                errors_info.append({"index": summary_task_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple summary tasks failed")

upsert_multiple_summary_tasks.__doc__ = f" upsert multiple summary_tasks".expandtabs()


# update summary_task
@router.put('/summary_task_id', tags=['summary_tasks'], status_code=HTTP_201_CREATED, summary="Update summary_task with ID", response_model=ReadSummary_Task)
async def update(request: Request, summary_task_id: UUID, summary_task: UpdateSummary_Task, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.update_roles())

    try:
        obj = await Summary_TaskModel.objects(db)
        data = await obj.get(id=summary_task_id)
        if not data:
            raise FileNotFoundError
        new_data = summary_task.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": data.to_dict() if data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        await obj.update(obj_id=summary_task_id, **kwargs)
        return data
    except FileNotFoundError:
        raise HTTPException(404, f"<{summary_task_id}> record not found in summary_tasks")
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed updating record with id <{summary_task_id}> in summary_tasks")

update.__doc__ = f" Update a summary_task by its id and payload".expandtabs()


# delete summary_task
@router.delete('/summary_task_id', tags=['summary_tasks'], status_code=HTTP_204_NO_CONTENT, summary="Delete summary_task with ID", response_class=Response)
async def delete(request: Request, summary_task_id: UUID, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.delete_roles())
    try:
        obj = await Summary_TaskModel.objects(db)
        old_data = await obj.get(id=summary_task_id)
        if not old_data:
            return JSONResponse(content={"message": f"<{summary_task_id}> record not found in summary_tasks"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Summary_TaskModel.objects(db)
        await obj.delete(obj_id=summary_task_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a summary_task by its id".expandtabs()


# delete multiple summary_tasks
@router.delete('/delete-summary_tasks', tags=['summary_tasks'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple summary_tasks with IDs", response_class=Response)
async def delete_multiple_summary_tasks(request: Request, summary_tasks_id: List[str] = QueryParam(), db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    log.debug('--- new request ---')
    log.debug(f"{str(request.method)}: {str(request.url)}")

    token.auth(Summary_TasksAccess.delete_roles())
    try:
        obj = await Summary_TaskModel.objects(db)
        all_old_data = await obj.get_multiple(obj_ids=summary_tasks_id)

        if not all_old_data:
            return JSONResponse(content={"message": f"<{summary_tasks_id}> record not found in summary_tasks"}, status_code=400)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": all_old_data if len(all_old_data) > 0 else [],
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Summary_TaskModel.objects(db)
        await obj.delete_multiple(obj_ids=summary_tasks_id, **kwargs)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"failed deleting summary_tasks_id <{summary_tasks_id}>")

delete.__doc__ = f" Delete multiple summary_tasks by list of ids".expandtabs()