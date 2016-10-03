# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


class IPunt(form.Schema):
    """ Tipus Punt: Per a cada Òrgan de Govern es podran crear
        tots els punts que es considerin oportunes
    """

    dexteritytextindexer.searchable('titlePunt')
    titlePunt = schema.TextLine(
        title=_(u'Punt Title'),
        required=True
    )


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IPunt)


class View(grok.View):
    grok.context(IPunt)
    grok.template('punt_view')

    def FilesInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        data = portal_catalog.searchResults(
            portal_type='File',
            path={'query': folder_path,
                  'depth': 1})

        # The last modified is the first shown.
        return sorted(data, key=lambda item: item.start, reverse=True)
