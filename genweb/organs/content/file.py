# -*- coding: utf-8 -*-
from five import grok
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from plone.namedfile.field import NamedBlobFile
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from plone import api
from zope import schema
from plone.app.dexterity import PloneMessageFactory as _PMF
from collective import dexteritytextindexer
from plone.supermodel.directives import fieldset
from plone.namedfile.utils import get_contenttype
from zope.schema import ValidationError

grok.templatedir("templates")


class InvalidPDFFile(ValidationError):
    """Exception for invalid PDF file"""
    __doc__ = _(u"Invalid PDF file")


class IFile(form.Schema):
    """ Tipus File: Per adjuntar els fitxers públics i/o privats
        A la part pública només fitxers PDF """

    fieldset('file',
             label=_(u'Tab file'),
             fields=['title', 'description', 'hiddenfile', 'visiblefile']
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

    dexterity.read_permission(hiddenfile='cmf.ReviewPortalContent')
    dexterity.write_permission(hiddenfile='cmf.ReviewPortalContent')
    hiddenfile = NamedBlobFile(
        title=_(u"Please upload a reserved file"),
        description=_(u"Reserved file description"),
        required=False,
    )

    visiblefile = NamedBlobFile(
        title=_(u"Please upload a public file"),
        description=_(u"Published file description"),
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

    def viewReservedFile(self):
        # Si tens rols Secretari, Editor, Membre o Manager el veus.
            username = api.user.get_current().id
            if username:
                roles = api.user.get_roles(username=username, obj=self.context)
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'Manager' in roles:
                    return True
                else:
                    return False
            else:
                return False
