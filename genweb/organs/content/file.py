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

grok.templatedir("templates")


class IFile(form.Schema):
    """ Tipus File: Per adjuntar els fitxers públics o privats """

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


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IFile)


class View(grok.View):
    grok.context(IFile)
    grok.template('file_view')

    def get_mimetype_icon_reserved(self):
        # return mimetype from the file object
        content_file = self.context.hiddenfile
        context = aq_inner(self.context)
        pstate = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state'
        )
        portal_url = pstate.portal_url()
        mtr = getToolByName(context, "mimetypes_registry")
        mime = []
        if content_file.contentType:
            mime.append(mtr.lookup(content_file.contentType))
        if content_file.filename:
            mime.append(mtr.lookupExtension(content_file.filename))
        mime.append(mtr.lookup("application/octet-stream")[0])
        icon_paths = [m.icon_path for m in mime if hasattr(m, 'icon_path')]
        if icon_paths:
            return icon_paths[0]

        return portal_url + "/" + guess_icon_path(mime[0])

    def get_mimetype_icon_public(self):
        # return mimetype from the file object
        content_file = self.context.hiddenfile
        context = aq_inner(self.context)
        pstate = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state'
        )
        portal_url = pstate.portal_url()
        mtr = getToolByName(context, "mimetypes_registry")
        mime = []
        if content_file.contentType:
            mime.append(mtr.lookup(content_file.contentType))
        if content_file.filename:
            mime.append(mtr.lookupExtension(content_file.filename))
        mime.append(mtr.lookup("application/octet-stream")[0])
        icon_paths = [m.icon_path for m in mime if hasattr(m, 'icon_path')]
        if icon_paths:
            return icon_paths[0]

        return portal_url + "/" + guess_icon_path(mime[0])

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

    def viewReservedFile(self):
        # Si tens rols Secretari, Editor, Membre o Manager el veus.
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if roles:
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'Manager' in roles:
                    return True
                else:
                    return False
            else:
                return False

    def viewPublicFile(self):
        # - Si tens rols Afectat, Anonim o Manager el veus.
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if roles:
                if 'OG4-Afectat' in roles or 'OG5-Anonim' in roles or 'Manager' in roles:
                    return True
                else:
                    return False
            else:
                return False
