# -*- coding: utf-8 -*-
import ast

from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.dexterity import textindexer
from plone import api
from Products.CMFPlone import PloneMessageFactory as _PMF
from z3c.form import form
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import get_contenttype
from plone.supermodel.directives import fieldset
from zope import schema
from zope.schema import ValidationError
from z3c.form import button
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils

import transaction

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.validator import SimpleFieldValidator
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityContent
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


class InvalidPDFFile(ValidationError):
    """Exception for invalid PDF file"""
    __doc__ = _(u"Invalid PDF file")


# @adapter(schema.interfaces.IField, IDexterityContent, schema.interfaces.IField)
class VisibleFileValidator(SimpleFieldValidator):
    def validate(self, value):
        """Valida que el archivo sea un PDF."""
        super().validate(value)
        if value is not None:
            mimetype = get_contenttype(value)
            if mimetype != 'application/pdf':
                raise InvalidPDFFile(mimetype)

# Define la función defaultFactory para el campo 'title'
@provider(IContextAwareDefaultFactory)
def title_default_factory(context):
    """Genera el valor predeterminado para el campo 'title'."""
    return context.Title()


class IFile(model.Schema):
    """ File: Per adjuntar els fitxers públics i/o privats
        A la part pública només fitxers PDF """

    fieldset('file',
             label=_(u'Tab file'),
             fields=['title', 'description', 'visiblefile', 'hiddenfile']
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True,
        defaultFactory=title_default_factory
    )

    textindexer.searchable('description')
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


# @form.validator(field=IFile['visiblefile'])
# def validateFileType(value):
#     if value is not None:
#         mimetype = get_contenttype(value)
#         if mimetype != 'application/pdf':
#             raise InvalidPDFFile(mimetype)


# @form.default_value(field=IFile['title'])
# def titleDefaultValue(data):
#     # ficar el títol de la sessió
#     return data.context.Title()


class Edit(form.EditForm):
    """A standard edit form. """

    # def update(self):
    #     sessio = utils.get_session(self.getContent())
    #     if sessio is not None:
    #         estat = utils.session_wf_state(sessio)
    #         if estat == 'tancada':
    #             raise Unauthorized

    # override handleApply
    @button.buttonAndHandler(_("Save"), name="save")
    def handleApply(self, action):
        """ Custom handleApply for save button
            If the file is replaced, the uploaded flag is set to False (for gDOC coherence)
        """
        super(Edit, self).handleApply.func(self, action)
        w_visiblefile = self.getWidget('visiblefile')
        w_hiddenfile = self.getWidget('hiddenfile')

        info_firma = getattr(self.context, 'info_firma', None) or {}
        if not isinstance(info_firma, dict):
            info_firma = ast.literal_eval(info_firma)

        if info_firma.get('public', {}).get('uploaded', False):
            if w_visiblefile.action() == 'replace':
                info_firma['public'].update({  # hará que aparezca el check de subir a gDOC con estado amarillo
                    'replaced': True,
                    'uploaded': False,
                    'error': 'El fitxer ha estat reemplaçat'
                })
                IStatusMessage(self.request).addStatusMessage(
                    _(u"El fitxer públic s'ha de pujar de nou a gDOC desde la vista 'Gestió signatura i arxiu gDOC"), "info success"
                )
                # Si las de organs quieren aquí podemos llamar la función para subir los ficheros a gDOC automáticamente
                # genweb.organs.firmadocumental.webservices.uploadFileGDoc
            elif w_visiblefile.action() == 'remove':
                info_firma.pop('public', None)

        if info_firma.get('private', {}).get('uploaded', False):
            if w_hiddenfile.action() == 'replace':
                info_firma['private'].update({  # hará que aparezca el check de subir a gDOC con estado amarillo
                    'replaced': True,
                    'uploaded': False,
                    'error': 'El fitxer ha estat reemplaçat'
                })
                IStatusMessage(self.request).addStatusMessage(
                    _(u"El fitxer restringit s'ha de pujar de nou a gDOC desde la vista 'Gestió signatura i arxiu gDOC"), "info success"
                )
                # Si las de organs quieren aquí podemos llamar la función para subir los ficheros a gDOC
                # genweb.organs.firmadocumental.webservices.uploadFileGDoc
            elif w_hiddenfile.action() == 'remove':
                info_firma.pop('private', None)
        self.context.info_firma = str(info_firma)
        transaction.commit()

    def getWidget(self, widget_name):
        """Get the widget by name."""
        widget = self.widgets.get(widget_name)
        if not widget:
            for group in self.groups:
                widget = group.widgets.get(widget_name)
                if widget:
                    break
        return widget


class View(BrowserView):
    index = ViewPageTemplateFile("templates/file_view.pt")

    def __call__(self):
        return self.index()

    def icon_type(self):
        """Devuelve el sufijo de Bootstrap Icon según mimetype."""
        ct = None
        if self.context.hiddenfile:
            ct = self.context.hiddenfile.contentType
        elif self.context.visiblefile:
            ct = self.context.visiblefile.contentType

        if not ct:
            return 'file-earmark'

        if 'application/pdf' in ct:
            return 'file-earmark-pdf'
        if 'audio/' in ct:
            return 'file-earmark-music'
        if 'video/' in ct:
            return 'file-earmark-play'
        if 'image/' in ct:
            return 'file-earmark-image'
        return 'file-earmark-text'

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

    def publicFileUploadedGdoc(self):
        info_firma = getattr(self.context, 'info_firma', None) or {}
        if not isinstance(info_firma, dict):
            info_firma = ast.literal_eval(info_firma)
        return info_firma.get('public', {}).get('uploaded', False)

    def privateFileUploadedGdoc(self):
        info_firma = getattr(self.context, 'info_firma', None) or {}
        if not isinstance(info_firma, dict):
            info_firma = ast.literal_eval(info_firma)
        return info_firma.get('private', {}).get('uploaded', False)

    def publicFileViewURL(self):
        if self.publicFileUploadedGdoc():
            return self.context.absolute_url() + '/viewFileGDoc?visibility=public'
        else:
            return self.context.absolute_url() + '/@@display-file/visiblefile/' + self.context.visiblefile.filename

    def privateFileViewURL(self):
        if self.privateFileUploadedGdoc():
            return self.context.absolute_url() + '/viewFileGDoc?visibility=private'
        else:
            return self.context.absolute_url() + '/@@display-file/hiddenfile/' + self.context.hiddenfile.filename

    def publicFileDownloadURL(self):
        if self.publicFileUploadedGdoc():
            return self.context.absolute_url() + '/downloadFileGDoc?visibility=public'
        else:
            return self.context.absolute_url() + '/@@download/visiblefile/' + self.context.visiblefile.filename

    def privateFileDownloadURL(self):
        if self.privateFileUploadedGdoc():
            return self.context.absolute_url() + '/downloadFileGDoc?visibility=private'
        else:
            return self.context.absolute_url() + '/@@download/hiddenfile/' + self.context.hiddenfile.filename

    def viewPublic(self):
        """ Cuando se muestra la parte pública del FICHERO
        """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organ_tipus = self.context.organType

        if self.context.visiblefile and self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(
                    ['OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'],
                        roles):
                    return False
                else:
                    return True
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG4-Afectat'],
                        roles):
                    return True
                else:
                    return False

        elif self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat',
                     'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False

        elif self.context.visiblefile:
            if organ_tipus == 'open_organ':
                return True
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
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
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat',
                     'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
        elif self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat',
                     'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if utils.checkhasRol(
                    ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'],
                        roles):
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
        return self.hihaReserved() and utils.checkhasRol(
            ['Manager', 'OG1-Secretari', 'OG2-Editor'],
            roles)

    def changePublic(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return self.hihaPublic() and utils.checkhasRol(
            ['Manager', 'OG1-Secretari', 'OG2-Editor'],
            roles)

    def canView(self):
        # Permissions to view FILE
        # If manager Show all
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(
                ['OG1-Secretari', 'OG2-Editor'],
                    roles):
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
            if estatSessio == 'planificada' and utils.checkhasRol(
                ['OG1-Secretari', 'OG2-Editor'],
                    roles):
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
            if estatSessio == 'planificada' and utils.checkhasRol(
                ['OG1-Secretari', 'OG2-Editor'],
                    roles):
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

    def sessionIsClosed(self):
        return utils.session_wf_state(self) == 'tancada'

    # ------------------------------------------------------------------
    # Outputs usados en la plantilla
    # ------------------------------------------------------------------

    def title(self):
        """Título a mostrar en la cabecera cuando procede."""
        return self.context.Title()

    def message(self):
        """Por ahora no se muestra contenido adicional, pero devolvemos
        cadena vacía para evitar LocationError en la plantilla."""
        return ""


class VisibleToHidden(BrowserView):
    def __call__(self):
        if utils.session_wf_state(self) == 'tancada':
            self.request.response.redirect(self.context.absolute_url())

        if self.context.visiblefile:
            self.context.hiddenfile = self.context.visiblefile
            self.context.visiblefile = None

        IStatusMessage(
            self.request).addStatusMessage(
            _(u'Visibilitat del fitxer modificada correctament.'),
            'info')

        info_firma = getattr(self.context, 'info_firma', None) or {}
        if not isinstance(info_firma, dict):
            info_firma = ast.literal_eval(info_firma)

        if info_firma.get('private', {}).get('uploaded', False):
            info_firma['private'].update({
                'replaced': True,
                'uploaded': False,
                'error': 'El fitxer ha estat reemplaçat'
            })
            IStatusMessage(self.request).addStatusMessage(
                _(u"El fitxer restringit s'ha de pujar de nou a gDOC desde la vista 'Gestió signatura i arxiu gDOC"), "info success"
            )

        if info_firma.get('public', {}).get('uploaded', False):
            info_firma.pop('public', None)

        self.context.info_firma = str(info_firma)
        self.context.reindexObject()
        transaction.commit()

        self.request.response.redirect(self.context.absolute_url())


class HiddenToVisible(BrowserView):
    def __call__(self):
        if utils.session_wf_state(self) == 'tancada':
            self.request.response.redirect(self.context.absolute_url())

        if self.context.hiddenfile:
            self.context.visiblefile = self.context.hiddenfile
            self.context.hiddenfile = None

        IStatusMessage(
            self.request).addStatusMessage(
            _(u'Visibilitat del fitxer modificada correctament.'),
            'info')

        info_firma = getattr(self.context, 'info_firma', None) or {}
        if not isinstance(info_firma, dict):
            info_firma = ast.literal_eval(info_firma)

        if info_firma.get('public', {}).get('uploaded', False):
            info_firma['public'].update({
                'replaced': True,
                'uploaded': False,
                'error': 'El fitxer ha estat reemplaçat'
            })
            IStatusMessage(self.request).addStatusMessage(
                _(u"El fitxer restringit s'ha de pujar de nou a gDOC desde la vista 'Gestió signatura i arxiu gDOC"), "info success"
            )

        if info_firma.get('private', {}).get('uploaded', False):
            info_firma.pop('private', None)

        self.context.info_firma = str(info_firma)
        self.context.reindexObject()
        transaction.commit()

        self.request.response.redirect(self.context.absolute_url())
