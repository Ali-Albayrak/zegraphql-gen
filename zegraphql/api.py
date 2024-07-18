import importlib
import os
from dotenv import load_dotenv
load_dotenv()
import strawberry
import uvicorn
from fastapi import FastAPI, Response
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from strawberry.fastapi import GraphQLRouter

from business.queries import Query
from business.mutations import Mutation
from core.depends import get_context
from core.logger import log
from core.custom_exceptions import TriggerException

app = FastAPI(title='karari')

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
    )

app.include_router(graphql_app, prefix="/graphql")


@app.get('/')
async def root():
    """Health check for API, anything except 200 means the API is not ready"""
    return {"message": "karari API, generated by ZeKoder"}


@app.exception_handler(TriggerException)
async def trigger_exception_handler(request: Request, exc: TriggerException):
    """
    customize TriggerException response
    """
    error_response = []
    if isinstance(exc.detail, list):
        for errors in exc.detail:
            errors_info = {"index": errors.get("index", 0)}
            for error in errors.get("errors", []):
                errors_info["type"] = "TriggerException"
                errors_info["trigger_name"] = error.get("trigger_name", 0)
                errors_info["message"] = error.get("message", 0)
                errors_info["details"] = error.get("details", 0)
            error_response.append(errors_info)
    elif isinstance(exc.detail, dict):
        error_response.append({
            "index": 0,
            "errors": [
                {
                    "type": "TriggerException",
                    "trigger_name": exc.detail.get("trigger_name", 0),
                    "message": exc.detail.get("message", 0),
                    "details": exc.detail.get("details", 0)
                }
            ]
        })
    else:
        error_response.append({
            "index": 0,
            "errors": [
                {
                    "type": "TriggerException",
                    "message": exc.detail
                }
            ]
        })
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": error_response}))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    customize request error response
    """
    error_response, errors_detail = [], {}
    for error_index, error in enumerate(exc.errors()):
        error_detail, error_info = {}, {}
        length = len(error.get("loc"))
        if length <= 1:
            error_detail["index"] = 0
            error_info["field_name"] = error.get("loc")[0]
            error_info["message"] = str(error.get("loc")[0]) + " " + error["msg"]
        elif length == 2 and isinstance(error.get("loc")[0], str):
            error_detail["index"] = 0
            error_info["field_name"] = error.get("loc")[1]
            error_info["message"] = "<" + str(error.get("loc")[1]) + ">" + " " + error["msg"]
        elif length == 2:
            error_detail["index"] = error.get("loc")[0]
            error_info["field_name"] = error.get("loc")[1]
            error_info["message"] = "<" + str(error.get("loc")[1]) + ">" + " " + error["msg"]
        elif length == 3:
            error_detail["index"] = error.get("loc")[1]
            error_info["field_name"] = error.get("loc")[2]
            error_info["message"] = "<" + str(error.get("loc")[2]) + ">" + " " + error["msg"]
        error_detail["errors"] = [error_info]
        if errors_detail.get(error_detail["index"]):
            errors_detail[error_detail["index"]].append(error_info)
        else:
            errors_detail[error_detail["index"]] = [error_info]
    for key, value in errors_detail.items():
        try:
            key = int(key)
        except:
            key = 0
        error_response.append({
            "index": int(key),
            "errors": value
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": error_response})
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    customize http exception response
    """
    error_response = []
    if isinstance(exc.detail, list):
        for errors in exc.detail:
            errors_info = {"index": errors.get("index", 0)}
            for error in errors.get("errors", []):
                errors_info["field_name"] = error.get("field_name", 0)
                errors_info["message"] = error.get("message", 0)
            error_response.append(errors_info)
    elif isinstance(exc.detail, dict):
        error_response.append({
            "index": 0,
            "errors": [
                {
                    "field_name": exc.detail.get("field_name", 0),
                    "message": exc.detail.get("message", 0)
                }
            ]
        })
    else:
        error_response.append({
            "index": 0,
            "errors": [
                {
                    "field_name": None,
                    "message": exc.detail
                }
            ]
        })
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": error_response}))


origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
allow_methods = os.environ.get('ALLOWED_METHODS', 'GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD').split(',')
allow_headers = os.environ.get('ALLOWED_HEADERS', 'Authorization,Content-Type').split(',')


# handle CORS preflight requests
@app.options('/{rest_of_path:path}')
async def preflight_handler(request: Request, rest_of_path: str) -> Response:
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = ''.join(origins)
    response.headers['Access-Control-Allow-Methods'] = ', '.join(allow_methods)
    response.headers['Access-Control-Allow-Headers'] = ', '.join(allow_headers)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.environ.get('PORT', 5000)),
        reload=bool(os.environ.get('UVICORN_RELOAD', True)),
        debug=bool(os.environ.get('UVICORN_DEBUG', True)),
        workers=int(os.environ.get('UVICORN_WORKERS', 1))
    )