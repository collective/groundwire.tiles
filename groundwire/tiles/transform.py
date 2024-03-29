from lxml import etree
from zope.interface import implements
from plone.transformchain.interfaces import ITransform
from repoze.xmliter.utils import getHTMLSerializer
from repoze.xmliter.serializer import XMLSerializer
from groundwire.tiles.utils import renderTiles


class ParseXML(object):
    """First stage in the 8000's chain: parse the content to an lxml tree
    encapsulated in an XMLSerializer.

    The subsequent steps in this package will assume their result inputs are
    XMLSerializer iterables, and do nothing if it is not. This also gives us
    the option to parse the content here, and if we decide it's not HTML,
    we can avoid trying to parse it again.
    """

    implements(ITransform)

    order = 8000

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        if self.request.get('plone.app.blocks.disabled', False):
            return None

        content_type = self.request.response.getHeader('Content-Type')
        if content_type is None or not content_type.startswith('text/html'):
            return None

        contentEncoding = self.request.response.getHeader('Content-Encoding')
        if contentEncoding and contentEncoding in ('zip', 'deflate',
                                                   'compress',):
            return None

        try:
            result = getHTMLSerializer(result, pretty_print=True,
                                       encoding=encoding)
            self.request['plone.app.blocks.enabled'] = True
            return result
        except (TypeError, etree.ParseError):
            return None


class IncludeTiles(object):
    """Turn a panel-merged page into the final composition by including tiles.
    Assumes the input result is an lxml tree and returns an lxml tree for
    later serialization.
    """

    implements(ITransform)

    order = 8500

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return None

    def transformUnicode(self, result, encoding):
        return None

    def transformIterable(self, result, encoding):
        if not self.request.get('plone.app.blocks.enabled', False) or \
            not isinstance(result, XMLSerializer):
            return None

        result.tree = renderTiles(self.request, result.tree)
        return result
