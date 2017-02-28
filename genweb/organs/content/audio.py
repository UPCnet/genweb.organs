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
from AccessControl import Unauthorized
from plone import api

grok.templatedir("templates")


class IAudio(form.Schema):
    """ Tipus File: Per marcar si són públics o privats """

    file = NamedBlobFile(
        title=_(u"Please upload a media file"),
        required=True,
    )


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IAudio)


class View(grok.View):
    grok.context(IAudio)
    grok.template('audio_view')

    def canView(self):
        """ Return true if user is Editor or Manager """
        username = api.user.get_current().getId()
        if username:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Editor' in roles or 'Manager' in roles:
                return True
            else:
                raise Unauthorized
        else:
            raise Unauthorized

    def get_mimetype_icon(self):
        # return mimetype from the file object
        content_file = self.context.file
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

    def is_videotype(self):
        ct = self.context.file.contentType
        return 'video/' in ct

    def is_audiotype(self):
        ct = self.context.file.contentType
        return 'audio/' in ct
