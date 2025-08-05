# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from plone.app.dexterity import textindexer
from zope import schema
from zope.schema import ValidationError

from plone import api
from Products.CMFPlone import PloneMessageFactory as _PMF
from z3c.form import form
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import get_contenttype
from plone.supermodel.directives import fieldset
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import Invalid
from z3c.form.validator import SimpleFieldValidator
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityContent
from zope.schema.interfaces import IField


class InvalidAnnexFile(ValidationError):
    """Exception for invalid annex file"""
    __doc__ = _(u"Invalid annex file")


# @adapter(IField, IDexterityContent, IField)
class AnnexFileValidator(SimpleFieldValidator):
    def validate(self, value):
        """Valida que el archivo sea un PDF."""
        super().validate(value)
        if value is not None:
            mimetype = get_contenttype(value)
            if mimetype != 'application/pdf':
                raise InvalidAnnexFile(mimetype)


class IAnnex(model.Schema):
    """ Annex: only annex files are permitted """

    fieldset('annex',
             label=_(u'Tab annex'),
             fields=['title', 'description', 'file']
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True,
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

    file = NamedBlobFile(
        title=_(u"Please upload a annex file"),
        description=_(u"Only PDF files are permitted."),
        required=True,
    )


# @form.validator(field=IAnnex['file'])
# def validateFileType(value):
#     if value is not None:
#         mimetype = get_contenttype(value)
#         if mimetype != 'application/pdf':
#             raise InvalidAnnexFile(mimetype)


class Edit(form.EditForm):
    """A standard edit form. """
    pass


class View(BrowserView):
    index = ViewPageTemplateFile("annex.pt")

    def __call__(self):
        return self.index()

    @property
    def title(self):
        """Devuelve el título del anexo."""
        return getattr(self.context, 'title', '')

    def canView(self):
        # Permissions to view annex
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus == 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus != 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        else:
            raise Unauthorized

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
        if self.context.file:
            ct = self.context.file.contentType
            return 'application/pdf' == ct
        else:
            return None

    def audio_reserved(self):
        if self.context.file:
            ct = self.context.file.contentType
            return 'audio/' in ct
        else:
            return None

    def video_reserved(self):
        if self.context.file:
            ct = self.context.file.contentType
            return 'video/' in ct
        else:
            return None

    def showTitle(self):
        if api.user.is_anonymous():
            return False
        return True
