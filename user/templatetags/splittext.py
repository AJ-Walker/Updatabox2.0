from django import template

register = template.Library()


@register.filter
def splittext(value, key):
  """
    Returns the value turned into a list.
  """
  return value.split(key)