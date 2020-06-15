from django import template

register = template.Library()


@register.filter
def status_readable_name(value, count):
    """Converts the underscore from a status name into a space and adds trait count for it"""
    readable_name = value.replace('_', ' ')
    return f"{readable_name} [{count}]"
