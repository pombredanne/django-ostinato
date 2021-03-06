from django import template
from ostinato.pages.models import Page


register = template.Library()


@register.inclusion_tag('pages/breadcrumbs.html')
def crumbs(page, obj=None):
    """
    Customize ostinato's default breadcrumbs a bit. Basically we allow for
    passing ``obj`` to the tag, telling it that we are looking at a object,
    below ``page``.

    TODO: Should we include this in the pages app navbar tag by default?
    """
    try:
        crumbs = Page.objects.get_breadcrumbs(for_page=page)
    except:
        return {}

    if obj:
        crumbs.append({
            'title': obj.title,
            'url': obj.get_absolute_url(),
        })

    return {'breadcrumbs': crumbs}