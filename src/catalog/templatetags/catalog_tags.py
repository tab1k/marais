from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    # If changing any filter (non-page param), reset pagination to first page.
    if any(k != 'page' for k in kwargs.keys()):
        query.pop('page', None)
    for key, value in kwargs.items():
        if value is None:
             if key in query:
                 del query[key]
        else:
            query[key] = value
    return query.urlencode()
