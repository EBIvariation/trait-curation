from django import template

register = template.Library()


def status_readable_name(value, count):
    """Converts the underscore from a status name into a space"""
    readable_name = value.replace('_', ' ')
    return f"{readable_name} [{count}]"


register.filter('status_readable_name', status_readable_name)
