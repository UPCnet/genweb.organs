# -*- coding: utf-8 -*-
from five import grok
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from plone.namedfile.field import NamedBlobFile
from plone import api
from zope import schema
from plone.app.dexterity import PloneMessageFactory as _PMF
from collective import dexteritytextindexer
from plone.supermodel.directives import fieldset
from plone.namedfile.utils import get_contenttype
from zope.schema import ValidationError
from AccessControl import Unauthorized
from genweb.organs import utils


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

    dexterity.read_permission(hiddenfile='cmf.ReviewPortalContent')
    dexterity.write_permission(hiddenfile='cmf.ReviewPortalContent')
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

    def is_videotype_reserved(self):
        ct = self.context.hiddenfile.contentType
        return 'video/' in ct

    def is_videotype_public(self):
        ct = self.context.visiblefile.contentType
        return 'video/' in ct

    def is_audiotype_reserved(self):
        ct = self.context.hiddenfile.contentType
        return 'audio/' in ct

    def is_audiotype_public(self):
        ct = self.context.visiblefile.contentType
        return 'audio/' in ct

    def hihaReserved(self):
        if self.context.hiddenfile:
            return True
        else:
            return False

    def hihaPublic(self):
        if self.context.visiblefile:
            return True
        else:
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
        if utils.isManager(self):
            return True
        organ_tipus = self.context.aq_parent.organType  # 1 level up
        if self.context.visiblefile and self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if utils.isMembre(self):
                    return False
                else:
                    return True
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isAfectat(self)):
                    return True
                else:
                    return False

        elif self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False

        elif self.context.visiblefile:
            if organ_tipus == 'open_organ':
                return True
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
        else:
            if not self.context.visiblefile and not self.context.hiddenfile:
                return None
            else:
                raise Unauthorized

    def viewReserved(self):
        """ Cuando se muestra la parte privada del FICHERO
        """
        if utils.isManager(self):
            return True
        organ_tipus = self.context.aq_parent.organType  # 1 level up
        if self.context.visiblefile and self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
        elif self.context.hiddenfile:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
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

    def canView(self):
        # Permissions to view FILE
        # If manager Show all
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.aq_parent.organType  # 1 level up
        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        elif organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized

        elif organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            else:
                raise Unauthorized

        else:
            raise Unauthorized
