from django import template

register = template.Library()


@register.simple_tag
def get_db_table_name(request, classToModel):
    pass
