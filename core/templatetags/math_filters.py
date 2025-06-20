"""
Custom template filters for mathematical operations.
"""

from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide value by arg."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage of value relative to total."""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0


@register.filter
def lookup(dictionary, key):
    """Lookup a value in a dictionary by key."""
    try:
        return dictionary.get(key, '')
    except AttributeError:
        return ''