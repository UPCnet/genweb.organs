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
from AccessControl import Unauthorized
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from time import strftime
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog
from Products.CMFCore.utils import getToolByName

from genweb.organs import utils

grok.templatedir("templates")


class IImpersonate(form.Schema):
    """ Define the fields of this form
    """


class ShowSessionAs(form.SchemaForm):
    grok.name('view_as_role')
    grok.context(ISessio)
    grok.template("impersonate_as")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    def getUserRole(self):
        # Només els rols Reponsable, Editor i Manager poden veure aquesta vista 
        role = self.request.form.get('id', '')
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Manager' in roles or 'OG1-Responsable' in roles or 'OG2-Editor' in roles:
            return role
        else:
            return False

    def simulation(self):
        # Obtenim rol usuari que cal veure i fer la simulació
        role = str(self.getUserRole())
        if role is 'False':
            return self.request.response.redirect(self.context.absolute_url())
        elif role == 'OG1-Responsable':
            return 'Responsable'
        elif role == 'OG2-Editor':
            return 'Editor'
        elif role == 'OG3-Membre':
            return 'Membre'
        elif role == 'OG4-Afectat':
            return 'Afectat'
        elif role == 'OG5-Anonim':
            return 'Anonim'
        else:
            return self.request.response.redirect(self.context.absolute_url())

    def isAfectat(self):
        if self.simulation() is 'Afectat':
            return True
        else:
            return False

    def isMembre(self):
        if self.simulation() is 'Membre':
            return True
        else:
            return False

    def isAnonim(self):
        if self.simulation() is 'Anonim':
            return True
        else:
            return False

    def isEditor(self):
        if self.simulation() is 'Editor':
            return True
        else:
            return False

    def isResponsable(self):
        if self.simulation() is 'Responsable':
            return True
        else:
            return False
