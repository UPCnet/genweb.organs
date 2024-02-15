# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from collective import dexteritytextindexer
from five import grok
from plone import api
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import get_contenttype
from plone.supermodel.directives import fieldset
from zope import schema
from zope.schema import ValidationError

from genweb.organs import _
from genweb.organs import utils

import transaction

grok.templatedir("templates")


class InvalidPDFFile(ValidationError):
    """Exception for invalid PDF file"""
    __doc__ = _(u"Invalid PDF file")


class IFile(form.Schema):
    """ File: Per adjuntar els fitxers públics i/o privats
        A la part pública només fitxers PDF """

    fieldset('file',
             label=_(u'Tab file'),
             fields=['title', 'description', 'visiblefile', 'hiddenfile']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_PMF(u'label_description', default=u'Summary'),
        description=_PMF(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    visiblefile = NamedBlobFile(
        title=_(u"Please upload a public file"),
        description=_(u"Published file description"),
        required=False,
    )

    hiddenfile = NamedBlobFile(
        title=_(u"Please upload a reserved file"),
        description=_(u"Reserved file description"),
        required=False,
    )


@form.validator(field=IFile['visiblefile'])
def validateFileType(value):
    if value is not None:
        mimetype = get_contenttype(value)
        if mimetype != 'application/pdf':
            raise InvalidPDFFile(mimetype)


@form.default_value(field=IFile['title'])
def titleDefaultValue(data):
    # ficar el títol de la sessió
    return data.context.Title()


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IFile)


class View(grok.View):
    grok.context(IFile)
    grok.template('file_view')

    def icon_type(self):
        if self.context.hiddenfile:
            ct = self.context.hiddenfile.contentType
            if 'application/pdf' in ct:
                return 'fa-file-pdf-o'
            elif 'audio/' in ct:
                return 'fa-file-audio-o'
            elif 'video/' in ct:
                return 'fa-file-video-o'
            elif 'image/' in ct:
                return 'fa-file-image-o'
            else:
                return 'fa-file-text-o'
        else:
            return None

    def pdf_reserved(self):
        if self.context.hiddenfile:
            ct = self.context.hiddenfile.contentType
            return 'application/pdf' == ct
        else:
            return None

    def audio_reserved(self):
        if self.context.hiddenfile:
            ct = self.context.hiddenfile.contentType
            return 'audio/' in ct
        else:
            return None

    def video_reserved(self):
        if self.context.hiddenfile:
            ct = self.context.hiddenfile.contentType
            return 'video/' in ct
        else:
            return None

    def hihaReserved(self):
        file = getattr(self.context, 'hiddenfile', None)
        if file is not None:
            return True
        return False

    def hihaPublic(self):
        file = getattr(self.context, 'visiblefile', None)
        if file is not None:
            return True
        return False

    def isPDFpublic(self):
        isPDF = False
        if self.context.visiblefile:
            if 'application/pdf' in self.context.visiblefile.contentType:
                isPDF = True
        return isPDF

    def isPDFprivat(self):
        isPDF = False
        if self.context.hiddenfile:
            if 'application/pdf' in self.context.hiddenfile.contentType:
                isPDF = True
        return isPDF

    def viewPublic(self):
        """ Cuando se muestra la parte pública del FICHERO
        """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organ_tipus = self.context.organType

        if self.context.visiblefile and self.context.hiddenfile:
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

        elif self.context.hiddenfile:
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

        elif self.context.visiblefile:
            if organ_tipus == 'open_organ':
                return True
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
        else:
            if not self.context.visiblefile and not self.context.hiddenfile:
                return None
            else:
                raise Unauthorized

    def showTitle(self):
        if api.user.is_anonymous():
            return False
        return True

    def viewReserved(self):
        """ Cuando se muestra la parte privada del FICHERO
        """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organ_tipus = self.context.organType

        if self.context.visiblefile and self.context.hiddenfile:
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
        elif self.context.hiddenfile:
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
        elif self.context.visiblefile:
            if organ_tipus == 'open_organ':
                return True
        else:
            if not self.context.visiblefile and not self.context.hiddenfile:
                return None
            else:
                raise Unauthorized


    def changeReserved(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return self.hihaReserved() and utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def changePublic(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return self.hihaPublic() and utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def canView(self):
        # Permissions to view FILE
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

        elif organ_tipus == 'restricted_to_members_organ':
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

        elif organ_tipus == 'restricted_to_affected_organ':
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

        else:
            raise Unauthorized


class VisibleToHidden(grok.View):
    grok.context(IFile)
    grok.name('visibleToHidden')
    grok.require('zope2.View')

    def render(self):
        if self.context.visiblefile:
            self.context.hiddenfile = self.context.visiblefile
            self.context.visiblefile = None
            self.context.reindexObject()
            transaction.commit()
        IStatusMessage(self.request).addStatusMessage(_(u'Visibilitat del fitxer modificada correctament.'), 'info')
        self.request.response.redirect(self.context.absolute_url())



class HiddenToVisible(grok.View):
    grok.context(IFile)
    grok.name('hiddenToVisible')
    grok.require('zope2.View')

    def render(self):
        if self.context.hiddenfile:
            self.context.visiblefile = self.context.hiddenfile
            self.context.hiddenfile = None
            self.context.reindexObject()
            transaction.commit()
        IStatusMessage(self.request).addStatusMessage(_(u'Visibilitat del fitxer modificada correctament.'), 'info')
        self.request.response.redirect(self.context.absolute_url())