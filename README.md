## photo-share

# alembic init migrations

# migrations/env.py ... set

# alembic revision --autogenerate -m 'Init'

# alembic upgrade head

# ---

packages: https://github.com/uriyyo/fastapi-pagination https://pypi.org/project/python-redis-rate-limit/

# ---

# logging:

'''

# from datetime import datetime

# import traceback

# from src.services.asyncdevlogging import async_logging_to_file

# await async_logging_to_file(f'\n500:\t{datetime.now()}\t{MSC500_DATABASE_CONNECT}\t{traceback.extract_stack(None, 2)[1][2]}')

'''

# ---

# http://0.0.0.0:8000

# http://0.0.0.0:8000/docs#

# http://0.0.0.0:8000/api/healthchecker

# ---

## pagination != "^0.12.3" !!! need poetry update

# ----

.\make.bat html
make html

# ----

pytest tests/test_root.py -v
pytest tests/test_route_auth.py -v
pytest tests/test_route_auth2.py -v
pytest tests/test_route_users.py -v
pytest tests/test_routes_comments.py -v
pytest tests/test_unit_repository_comments.py -v

# -------------------
