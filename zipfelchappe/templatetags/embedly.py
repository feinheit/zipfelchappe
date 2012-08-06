import re
import json
import urllib2
from hashlib import sha1

from django.core.cache import cache
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django import template

register = template.Library()

@register.filter(is_safe=True)
def embedly(url, size='640x480'):
    """ A very minimalistic implementation of embedly oembed content """

    size_match = re.match(r'^(?P<width>\d+)x(?P<height>\d+)$', size)

    if not size_match:
        raise Exception('Could not parse size, should be <width>x<height>')

    maxsizes = size_match.groupdict()

    params = {
        'url': url,
        'maxwidth': maxsizes['width'],
        'maxheight': maxsizes['height']
    }

    embedly_url = 'http://api.embed.ly/1/oembed?%s' % urlencode(params)
    cache_key = 'embedly_%s' % sha1(embedly_url).hexdigest()

    result = cache.get(cache_key)

    if not result:
        try:
            request = urllib2.urlopen(embedly_url)
            response = request.read()
            data = json.loads(response)
            result = mark_safe(data['html'])
            cache.set(cache_key, result)
        except urllib2.URLError:
            return mark_safe('<p>External content could not be loaded...</p>')

    return result
