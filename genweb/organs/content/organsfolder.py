# -*- coding: utf-8 -*-
from five import grok
from plone import api
from plone.app.textfield import RichText as RichTextField
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from zope import schema

from genweb.organs import _
from genweb.organs import utils

grok.templatedir("templates")


class IOrgansfolder(form.Schema):
    """ Organs Folder: Carpeta Unitat que conté Organs de Govern
    """

    informationText = RichTextField(
        title=_(u"Text informatiu"),
        description=_(u'Text que es veurà quan el directori no conté cap Organ de Govern visible'),
        required=False,
    )

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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.organgovern',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []

        if api.user.is_anonymous():
            username = None
        else:
            username = api.user.get_current().id
        for obj in values:
            value = obj.getObject()
            organType = value.organType
            if username:
                roles = api.user.get_roles(obj=value, username=username)
            else:
                roles = []
            # If Manager or open bypass and list all
            if 'Manager' in roles or (organType == 'open_organ'):
                results.append(dict(title=value.title,
                                    absolute_url=value.absolute_url(),
                                    acronim=value.acronim,
                                    organType=value.organType,
                                    review_state=obj.review_state))
            # if restricted_to_members_organ
            elif organType == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))
            # if restricted_to_affected_organ
            elif organType == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        acronim=value.acronim,
                                        organType=value.organType,
                                        review_state=obj.review_state))

        return results

    def canView(self):
        # Permissions per veure l'estat dels organs a la taula principal
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)
