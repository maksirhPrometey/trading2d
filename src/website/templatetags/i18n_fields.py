from django import template

register = template.Library()


@register.filter
def loc(obj, field):
    """{{ product|loc:'name' }} — локалізоване поле моделі з fallback на uk."""
    if obj is None:
        return ''
    getter = getattr(obj, 'loc', None)
    if callable(getter):
        return getter(field)
    return getattr(obj, field, '') or ''
