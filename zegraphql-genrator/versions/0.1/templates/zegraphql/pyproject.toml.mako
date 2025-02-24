[tool.poetry]
name = "${app_name}"
version = "${version}"
description = ""
authors = ["ZeKoder <dev@zekoder.com>"]

[tool.poetry.dependencies]
python = "^3.10"
uvicorn = "^0.17.6"
requests = "~2.28"

psycopg2-binary = "^2.9.3"
asyncpg = "^0.28.0"
httpx = "^0.25.0"
python-dotenv = "^1.0.0"
pyjwt = "^2.8.0"
sqlalchemy = "^2.0.31"
strawberry-graphql = {extras = ["fastapi"], version = "^0.235.2"}


[tool.poetry.group.test]
optional = true

[tool.poetry.group.test.dependencies]
pytest = "^5.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"