import datetime
from typing import Optional, Union, List, Any

from fastapi import HTTPException, status
from mongosql import MongoQuery, InvalidColumnError, MongoQuerySettingsDict
from mongosql.handlers import MongoFilter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from core.depends import current_user_roles, current_user_uuid, current_user_tenant, get_sync_db

from .logger import log

# add custom $contains filter handler in py-mongosql
MongoFilter.add_scalar_operator(
    '$contains',
    lambda col, val, oval: col.ilike(val)
)
MongoFilter.add_scalar_operator(
    '$like',
    lambda col, val, oval: col.like(val)
)


class ColumnNotFound(Exception):
    pass


class UnkownOperator(Exception):
    pass


class QueryOperator(BaseModel):
    gt: Optional[Union[int, float, datetime.date, datetime.datetime]] = Field(None, title="> operator", alias="$gt")
    gte: Optional[Union[int, float, datetime.date, datetime.datetime]] = Field(None, title=">= operator", alias="$gte")
    lt: Optional[Union[int, float, datetime.date, datetime.datetime]] = Field(None, title="< operator", alias="$lt")
    lte: Optional[Union[int, float, datetime.date, datetime.datetime]] = Field(None, title="<= operator", alias="$lte")
    ne: Optional[Union[str, int, float, datetime.date, datetime.datetime]] = Field(None, title="!= operator", alias="$ne")
    prefix: Optional[str] = Field(None, title="value start with", alias="$prefix")
    contains: Optional[str] = Field(None, title="value contains this", alias="$contains")
    in_: Optional[list] = Field(None, title="value in this list", alias="$in")
    nin: Optional[list] = Field(None, title="value not in this list", alias="$nin")
    like: Optional[str] = Field(None, title="value like this", alias="$like")
    exist: Optional[bool] = Field(None, title="value null or not", alias="$exist")


class QueryAggregateFunc(BaseModel):
    min: Optional[str] = Field(None, title="find min of given field", alias="$min")
    max: Optional[str] = Field(None, title="find max of given field", alias="$max")
    sum: Optional[str] = Field(None, title="find sum of given field", alias="$sum")
    avg: Optional[str] = Field(None, title="find avg of given field", alias="$avg")
    group: Optional[List[str]]


class QuerySchema(BaseModel):
    project: Optional[list[str]]
    limit: Optional[int] = Field(20)
    skip: Optional[int] = Field(0)
    filter: Optional[Union[dict[str, Union[QueryOperator, List[dict[str, Union[QueryOperator, str]]], Any]]]]  # noqa
    sort: Optional[List[str]]
    join: Optional[Union[list, dict]]
    aggregate: Optional[dict]
    group: Optional[List[str]]
    count: Optional[int] = 1

    class Config:
        json_schema_extra = {
            "example": {
                "project": ["string"],
                "limit": 20,
                "skip": 0,
                "filter": {
                  "column name": "value"
                },
                "sort": [
                  "string"
                ],
                "join": {
                    "relation_column": {
                        "project": ["string"],
                        "limit": 20,
                        "skip": 0,
                        "filter": {
                          "column name": "value"
                        },
                        "sort": [
                            "string"
                        ],
                    }
                },
                "aggregate": {
                    "column_min": {"$min": "column"}
                },
                "group": ["string"],
                "count": 1
            }
        }


class BooleanOperatorFilters(BaseModel):
    or_: Optional[List[dict[str, Union[QueryOperator, str]]]] = Field(None, title="any is true", alias="$or")


class JSONQ:
    def __init__(self, session: Session, model) -> None:
        self.model = model
        self.session = session
        # self.session.execute(f"SET zekoder.id = '{current_user_uuid()}'")
        # self.session.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")
        # self.session.execute(f"SET zekoder.tenant_id = '{current_user_tenant()}'")

    def query(self, req: QuerySchema, allowed_aggregates: list[str]):
        try:
            result, aggregates, data, count = None, None, None, None
            # for aggregate actions.
            if req.aggregate:
                # let's get last element of the dict, we need that for success count
                # We assume that last element should be count action and most usage for
                # sql language it should be the last element in the query before FROM :)!
                last_element_key, last_element_val = list(req.aggregate.items())[-1]
                last_element = {last_element_key: last_element_val}
                # Calculating COUNT in reg.aggregate
                count = MongoQuery(self.model, MongoQuerySettingsDict(
                    aggregate_columns=allowed_aggregates,
                    aggregate_labels=True
                )).with_session(self.session).query(
                    filter=req.filter,
                    aggregate=last_element,
                ).end().first()[0]

                # data for aggregate actions
                data = MongoQuery(self.model, MongoQuerySettingsDict(
                    aggregate_columns=allowed_aggregates,
                    aggregate_labels=True,
                )).with_session(self.session).query(
                    filter=req.filter,
                    aggregate=req.aggregate,
                    group=req.group
                ).end().all()

            # for none aggregate actions
            if not req.aggregate:
                # if not aggregate then this is what we are going to do when getting cumulative count
                count_query = req.dict(by_alias=True, exclude_none=True)
                count = MongoQuery(self.model).with_session(self.session).query(**count_query).end().first()[0]
                # we should move count if we want to get all rows
                query = req.dict(by_alias=True, exclude={"count"}, exclude_none=True)
                data = MongoQuery(self.model).with_session(self.session).query(**query).end().all()

        except InvalidColumnError as e:
            log.debug(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={
                "field_name": e.where,
                "message": e.__str__()
            })
        except Exception as e:
            log.debug(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
        return {"data": data, "count": count if count else 0}
