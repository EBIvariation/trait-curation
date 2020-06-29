from django import template

register = template.Library()


@register.filter
def get_dict_item(dictionary, key):
    attribute_dict = dictionary.get(key)
    return attribute_dict['class']


@register.filter
def status_readable_name(value):
    """Converts the underscore from a status name into a space and adds trait count for it"""
    return value.replace('_', ' ')


@register.filter
def status_readable_name_with_count(value, count):
    """Converts the underscore from a status name into a space and adds trait count for it"""
    readable_name = value.replace('_', ' ')
    return f"{readable_name} [{count}]"
