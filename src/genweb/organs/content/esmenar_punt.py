# -*- coding: utf-8 -*-
from plone import api
from zope.schema import TextLine
from z3c.form import button
from z3c.form import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from plone.autoform import directives
from zope import schema
from z3c.form.interfaces import DISPLAY_MODE
from genweb.organs.utils import addEntryLog
from AccessControl import Unauthorized
from plone.event.interfaces import IEventAccessor
from genweb.organs import utils
import unicodedata
from plone.supermodel import model


class IEsmenar(model.Schema):
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

class Message:

	def __init__(self, context, request):
		self.context = context
		self.request = request

	def update(self):

		if api.user.is_anonymous() is True:
			raise Unauthorized
		else:
			username = api.user.get_current().id
			roles = api.user.get_roles(username=username, obj=self.context)
			if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
				self.request.set('disable_border', True)
			else:
				raise Unauthorized
