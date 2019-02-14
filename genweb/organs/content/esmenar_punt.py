# -*- coding: utf-8 -*-
from plone import api
from five import grok
from zope.schema import TextLine
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from z3c.form.interfaces import DISPLAY_MODE
from genweb.organs.utils import addEntryLog
from AccessControl import Unauthorized
from plone.event.interfaces import IEventAccessor
import unicodedata

grok.templatedir("templates")


class IEsmenar(form.Schema):
    """ Enviar missatge als membres /mail_message
    """
    name = TextLine(
        title=_("Nom complet"),
        description=_("Escriu el teu nom complet"),
        required=True)

    email = TextLine(
        title=_(u"Adreça de correu electrònic"),
        required=True)

    comments = schema.Text(
        title=_(u"Comentaris"),
        required=True,
    )

class Message(form.SchemaForm):

	grok.name('esmenes_punt_od')
	grok.context(ISessio)
	grok.template("esmenespunt_view")
	grok.require('zope2.View')
	grok.layer(IGenwebOrgansLayer)

	ignoreContext = True
	schema = IEsmenar

	def update(self):

		if api.user.is_anonymous() is True:
			raise Unauthorized
		else:
			username = api.user.get_current().id
			roles = api.user.get_roles(username=username, obj=self.context)
			if 'OG2-Editor' in roles or 'OG1-Secretari' in roles or 'OG3-Membre' in roles:
				self.request.set('disable_border', True)
				super(Message, self).update()
			else:
				raise Unauthorized