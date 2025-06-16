# -*- coding: utf-8 -*-
from zope import schema
from z3c.form import form
from genweb.organs import _
from plone.app.dexterity import textindexer
from plone.autoform import directives
from plone import api
from Products.CMFPlone import PloneMessageFactory as _PMF
from plone.supermodel.directives import fieldset
from AccessControl import Unauthorized
from genweb.organs import utils
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.supermodel import model
from plone.app.textfield import RichText as RichTextField

# Define la función defaultFactory para el campo 'title'
def title_default_factory(context):
    """Genera el valor predeterminado para el campo 'title'."""
    return context.Title()

class IDocument(model.Schema):
    """ Document: Per marcar si són públics o privats """

    fieldset('document',
             label=_(u'Tab document'),
             fields=['title', 'description', 'defaultContent', 'alternateContent']
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True,
        defaultFactory=title_default_factory
    )

    textindexer.searchable('description')
    description = RichTextField(
        title=_PMF(u'label_description', default=u'Summary'),
        description=_PMF(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    textindexer.searchable('defaultContent')
    defaultContent = RichTextField(
        title=_(u"Contingut public"),
        description=_(u"Default content shown in the document view"),
        required=False,
    )

    textindexer.searchable('alternateContent')
    alternateContent = RichTextField(
        title=_(u"Alternate description"),
        description=_(u"Content used to hide protected content"),
        required=False,
    )


# @form.default_value(field=IDocument['title'])
# def titleDefaultValue(data):
#     # fica el títol de document
#     return data.context.Title()


class Edit(form.EditForm):
    """A standard edit form. """
    pass


class View(BrowserView):
    index = ViewPageTemplateFile("templates/document_view.pt")

    def __call__(self):
        return self.index()

    def showTitle(self):
        if api.user.is_anonymous():
            return False
        return True

    def viewDocumentPublic(self):
        """ Cuando se muestra la parte pública del documento
        """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organ_tipus = self.context.organType

        if self.context.defaultContent and self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(['OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    return False
                else:
                    return True
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG4-Afectat'], roles):
                    return True
                else:
                    return False
        elif self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
        elif self.context.defaultContent:
            if organ_tipus == 'open_organ':
                return True
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
        else:
            raise Unauthorized

    def viewDocumentReserved(self):
        """ Cuando se muestra la parte privada del documento
        """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organ_tipus = self.context.organType

        if self.context.defaultContent and self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
        elif self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
        elif self.context.defaultContent:
            if organ_tipus == 'open_organ':
                    return True
        else:
            raise Unauthorized

    def canView(self):
        # Permissions to view DOCUMENT
        # If manager Show all
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada':
                return True
            elif estatSessio == 'realitzada':
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized
