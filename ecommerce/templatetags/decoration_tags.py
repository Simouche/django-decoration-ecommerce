from django import template

register = template.Library()


@register.filter(name='subtract')
def subtract(value, arg):
    if isinstance(value, str):
        if len(value) == 0:
            value = 0
        else:
            value = int(value)
    if isinstance(arg, str):
        if len(arg) == 0:
            arg = 0
        else:
            arg = int(arg)
    return value - arg
