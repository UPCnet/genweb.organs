# -*- coding: utf-8 -*-
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from genweb.organs import _
from zope import schema
grok.templatedir("templates")


class IOrgansfolder(form.Schema):
    """ Tipus Organs Folder: Carpeta que conté Organs
    """

    customImage = schema.Bool(
        title=_(u'Fer servir capcalera personalitzada?'),
        description=_(u'Si es vol fer servir la imatge estandard o la imatge que es puja a continuació'),
        required=False,
        default=False,
    )

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
        values = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.organgovern',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            results.append(dict(title=value.title,
                                absolute_url=value.absolute_url(),
                                acronim=value.acronim,
                                tipus=value.tipus,
                                review_state=obj.review_state))
        return results
