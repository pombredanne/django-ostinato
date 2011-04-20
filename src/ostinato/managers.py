from django.db import models
from django.contrib.contenttypes.models import ContentType

class ContentItemManager(models.Manager):
    def create_for(self, object_instance, **kwargs):
        """
        A custom create method which will create a new ContentItem,
        that will point directly to another ContentType.
        
        ``object_instance`` will be the item we wish to create a new
        ContentItem instance for.
        
        Once created return the instance of the new content_item.
        """
        ctype = ContentType.objects.get_for_model(object_instance)
        content_item = self.get_query_set().create(
            content_type=ctype,
            object_id=object_instance.id,
            **kwargs
        )
        content_item.save()
        return content_item

    def _get_parents(self, item):
        if item.parent:
            yield item.parent
            self._get_parents(item.parent)

    def get_navbar(self, parent=None, depth=0):
        """
        Returns a dictionary of items with their titles and urls.

        ``parent`` is an instance of ContentItem. If specified, will only
        return items that has ``parent`` set as the ``parent`` for that
        item.

        """
        to_return = []
        nav_items = self.get_query_set().filter(
            parent=parent, show_in_nav=True, _sm_state='Published')
        if nav_items:
            for item in nav_items:
                to_return.append({
                    'title': item.get_short_title(),
                    'url': item.get_absolute_url(),
                })
        return to_return

    def get_breadcrumbs(self, content_item):
        """
        Returns the breadcrumbs for the current ``content_item``
        The returned value is a list containing a dictionary for each
        item.

        """
        to_return = []
        parents = [parent for parent in self._get_parents(content_item)]
        if parents and not(None in parents):
            to_return += [{
                'title': parent.get_short_title(),
                'url': parent.get_absolute_url(),
                'current': False,
            } for parent in parents]
        to_return.append({
            'title': content_item.get_short_title(),
            'url': content_item.get_absolute_url(),
            'current': True,
        })
        return to_return
