<%def name="get_pascal_case_without_underscore(text)">\
<% return text.replace("-"," ").replace("_", " ").title().replace(" ","") %>
</%def>
