from django import template

import forum.scripts.trunc_number as scripts

register = template.Library()


# make slice of given string just like python does
@register.filter(name='trunc')
def trunc(value, arg):
    value = str(value)
    arg = str(arg)

    try:
        if ':' in arg:
            interval = arg.split(':')
            start = int(interval[0])
            if not start:
                start = 0
            finish = int(interval[1])
        else:
            start = 0
            finish = int(arg)

        if start:
            return value[start:finish]
        else:
            return value[:finish]

    except ValueError:
        pass


@register.filter(name='trunc_number')
def trunc_number(value):
    return scripts.trunc_number(value)
