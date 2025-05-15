# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from z3c.form import form, button
from z3c.form.interfaces import DISPLAY_MODE
from zope import schema
from zope.schema import TextLine
from plone.autoform import directives
from plone.supermodel import model

from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs.utils import addExcuse
from genweb.organs import utils


class IExcusar(model.Schema):
    name = TextLine(
        title=_(u"Nom i cognoms"),
        required=False)

    email = TextLine(
        title=_(u"Correu electrònic"),
        required=False)

    comments = schema.Text(
        title=_(u"Comentaris"),
        description=_(u"Descriu el motiu pel qual no pots assistir a la sessió"),
        required=True,
    )


class Message(form.Form):
    ignoreContext = True
    schema = IExcusar

    def update(self):
        """  Disable the view if username has no roles.
             Send Message if user is Editor / Secretari / Manager """
        if api.user.is_anonymous() is True:
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG3-Membre', 'OG5-Convidat'], roles):
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized

    def updateWidgets(self):
        super(Message, self).updateWidgets()

        user = api.user.get_current().id
        acl_users = getToolByName(self.context, 'acl_users')
        getLdapUser = acl_users.ldapUPC.acl_users.searchUsers

        try:
            self.widgets["name"].value = getLdapUser(dn='cn=' + user + ',ou=Users,dc=upc,dc=edu')[0]['sn']
            self.widgets["email"].value = getLdapUser(dn='cn=' + user + ',ou=Users,dc=upc,dc=edu')[0]['mail']
            self.widgets["name"].mode = DISPLAY_MODE
            self.widgets["email"].mode = DISPLAY_MODE
        except:
            self.widgets["name"].value = ""
            self.widgets["email"].value = ""

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):
        """ Send the email to the configured mail address
            in properties and redirect to the
            front page, showing a status message to say
            the message was received. """
        formData, errors = self.extractData()
        lang = self.context.language
        if 'comments' not in formData:
            if lang == 'ca':
                message = "Falten camps obligatoris: "
            if lang == 'es':
                message = "Faltan campos obligatorios: "
            if lang == 'en':
                message = "Required fields missing: "
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return

        addExcuse(self.context, self.widgets["name"].value or formData['name'], self.widgets["email"].value or formData['email'], self.widgets["comments"].value)

        self.context.plone_utils.addPortalMessage(_(u"Missatge enviat correctament"), 'info')

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
