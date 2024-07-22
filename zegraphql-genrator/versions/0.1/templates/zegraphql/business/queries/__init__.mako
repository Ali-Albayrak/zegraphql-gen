from strawberry.tools import merge_types

<%
# Helper function to generate the import statements and the class names for merging
def generate_imports_and_classes(data):
    imports = []
    classes = []
    for obj_name, obj_details in data.items():
        query_name = get_pascal_case_without_underscore(obj_name) + 'Query'
        import_statement = f"from .{obj_name} import {query_name}"
        imports.append(import_statement)
        classes.append(query_name)
    return imports, classes
%>

<%
imports, classes = generate_imports_and_classes(data)
%>

% for import_statement in imports:
${import_statement}
% endfor

Query = merge_types('Query', (
% for class_name in classes:
    ${class_name},
% endfor
))
