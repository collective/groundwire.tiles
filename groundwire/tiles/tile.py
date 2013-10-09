from AccessControl import getSecurityManager
from zope.interface import Interface

from plone import tiles
from zope.schema import Text
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer


class IRichTextTileData(Interface):

    text = RichText(title=u'Text', required=False)


class RichTextTile(tiles.PersistentTile):

    def __call__(self):
        can_edit = getSecurityManager().checkPermission('Modify portal content', self.context)
        self.request.response.setHeader('X-Tile-Editable', '1' if can_edit else '0')
        text = ''
        if self.data['text']:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data['text'], 'text/x-html-safe')
        return '<html><body>%s</body></html>' % text


class IPlainTextTileData(Interface):

    text = Text(title=u"Text", required=False)


class PlainTextTile(tiles.PersistentTile):

    def __call__(self):
        can_edit = getSecurityManager().checkPermission('Modify portal content', self.context)
        self.request.response.setHeader('X-Tile-Editable', '1' if can_edit else '0')
        text = ''
        if self.data['text']:
            text = self.data['text']
        return '<html><body>%s</body></html>' % text
