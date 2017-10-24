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
    """ Carpeta unitat VIEW form
    """

    grok.context(IOrgansfolder)
    grok.template('organsfolder_view')

    def OrgansInside(self):
        """ Retorna els organs de govern depenent del rol
            i l'estat de l'Organ. Per això fa 3 cerques
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.organgovern',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        from plone import api

        if api.user.is_anonymous():
            username = None
            roles = []
        else:
            username = api.user.get_current().id
        for obj in values:
            value = obj.getObject()
            organType = value.organType
            roles = api.user.get_roles(obj=value, username=username)

            # If Manager or open bypass and list all
            if 'Manager' in roles or (organType == 'open_organ'):
                results.append(dict(title=value.title,
                                    absolute_url=value.absolute_url(),
                                    acronim=value.acronim,
                                    organType=value.organType,
                                    review_state=obj.review_state))
            # if restricted_to_members_organ
            elif organType == 'restricted_to_members_organ':
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles:
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))
            # if restricted_to_affected_organ
            elif organType == 'restricted_to_affected_organ':
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))

        return results

    def canView(self):
        # Permissions per veure l'estat dels organs a la taula principal
        if utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self):
            return True
        else:
            return False
