from strawberry.tools import merge_types
from .documents import DocumentQuery
from .industries import IndustryQuery

Query = merge_types('Query', (DocumentQuery, IndustryQuery))