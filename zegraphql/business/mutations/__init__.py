from strawberry.tools import merge_types
from .documents import DocumentMutation
from .industries import IndustryMutation

Mutation = merge_types('Mutation', (DocumentMutation, IndustryMutation))
