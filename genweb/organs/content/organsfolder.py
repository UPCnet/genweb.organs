# -*- coding: utf-8 -*-
from five import grok
from genweb.organs import _
from genweb.organs import utils
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from zope import schema

grok.templatedir("templates")


class IOrgansfolder(form.Schema):
    """ Organs Folder: Carpeta Unitat que conté Organs de Govern
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
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.organgovern',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            value = obj.getObject()
            organType = value.organType
            # If Manager or Obert bypass and list all
            if utils.isManager(self) or (organType == 'open_organ'):
                results.append(dict(title=value.title,
                                    absolute_url=value.absolute_url(),
                                    acronim=value.acronim,
                                    organType=value.organType,
                                    review_state=obj.review_state))
            # if restricted_to_members_organ
            elif organType == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))
            # if restricted_to_affected_organ
            elif organType == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))

        return results
