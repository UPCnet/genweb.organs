# -*- coding: utf-8 -*-
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from genweb.organs import _


class IOrgansfolder(form.Schema):
    """ Tipus Organs Folder: Carpeta que conté Organs
    """

    logoOrganFolder = NamedBlobImage(
        title=_(u"Organs folder logo"),
        description=_(u'Logo organs folder description'),
        required=False,
    )


class View(grok.View):
    grok.context(IOrgansfolder)
    grok.template('organsfolder_view')

    def OrgansInside(self):
        """ Retorna els organs de govern
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        data = portal_catalog.searchResults(
            portal_type='genweb.organs.organgovern',
            path={'query': folder_path,
                  'depth': 1})

        # The last modified is the first shown.
        return sorted(data, key=lambda item: item.start, reverse=True)
