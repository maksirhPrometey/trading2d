from django import template

from src.website.html_sanitize import render_richtext

register = template.Library()


@register.filter(name='richtext')
def richtext(value):
    return render_richtext(value)
