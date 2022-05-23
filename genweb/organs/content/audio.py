# -*- coding: utf-8 -*-
from five import grok
from plone.directives import dexterity
from plone.directives import form
from zope import schema
from genweb.organs import _
from plone.namedfile.field import NamedBlobFile
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from collective import dexteritytextindexer
from plone.app.dexterity import PloneMessageFactory as _PMF
from AccessControl import Unauthorized
from plone.supermodel.directives import fieldset
from plone import api
from plone.namedfile.utils import get_contenttype
from zope.schema import ValidationError
from genweb.organs import utils


grok.templatedir("templates")


class InvalidAudioFile(ValidationError):
    """Exception for invalid audio file"""
    __doc__ = _(u"Invalid audio file")


class IAudio(form.Schema):
    """ Audio: only audio files are permitted """

    fieldset('audio',
             label=_(u'Tab audio'),
             fields=['title', 'description', 'file']
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

    file = NamedBlobFile(
        title=_(u"Please upload a media file"),
        description=_(u"Only audio files are permitted."),
        required=True,
    )


@form.validator(field=IAudio['file'])
def validateAudioType(value):
    if value is not None:
        mimetype = get_contenttype(value)
        if mimetype.split('/')[0] != 'audio':
            # If opus file permit it...
            if value.filename.split('.')[-1:][0] != 'opus' and get_contenttype(value) != 'application/octet-stream':
                raise InvalidAudioFile(mimetype)


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IAudio)


class View(grok.View):
    grok.context(IAudio)
    grok.template('audio_view')

    def canView(self):
        # Permissions to view audio
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

    def is_opusfile(self):
        # Check if the file is OPUS type
        ct = self.context.file.contentType
        ext = self.context.file.filename.split('.')[-1:][0]
        if ct == 'application/octet-stream' and ext == 'opus':
            return True
        else:
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
