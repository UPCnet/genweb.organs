# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from plone.namedfile.field import NamedBlobFile
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from plone import api
from zExceptions import Unauthorized
from genweb.organs import utils

grok.templatedir("templates")


class IFile(form.Schema):
    """ Tipus File: Per marcar si són públics o privats """

    hiddenfile = schema.Bool(
        title=_(u"Es tracta d'un fitxer privat?"),
        description=_(u'Per defecte els fitxers són privats. Si vol fer públic el fitxer, cal desmarcar aquesta opció.'),
        defaultFactory=lambda: True,
        required=False,
    )

    file = NamedBlobFile(
        title=_(u"Please upload a document"),
        required=True,
    )


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IFile)


class View(grok.View):
    grok.context(IFile)
    grok.template('file_view')

    def isPrivate(self):
        # Returns True if is a Private File
        if self.context.hiddenfile:
            return True
        return False

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

    def hihaFile(self):
        try:
            self.context.file.filename
            return True
        except:
            return False

    def canViewContent(self):
        # - Si el fitxer està marcat com a públic ho veu tothom
        # - Si tens rols Responsable, Editor, Membre o Manager encara que
        #   estigui marcat com a privat el veus.
        try:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG1-Responsable' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'Manager' in roles:
                return True
            elif self.context.hiddenfile is False:
                return True
            else:
                raise Unauthorized
        except:
            raise Unauthorized

    def showMessage(self):
        if utils.isAnonim(self) or utils.isAfectat(self):
            return False
        else:
            return True
