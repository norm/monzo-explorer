from django import template

register = template.Library()


@register.filter(is_safe=True)
def currency(value):
    return "%.2f" % (value / 100)
