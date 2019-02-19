# -*- coding: utf-8 -*-
from plone import api
from five import grok
from zope.schema import TextLine
from plone.namedfile.field import NamedBlobFile
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from zope import schema
from genweb.organs.utils import addPoint
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from Products.CMFPlone.utils import _createObjectByType
from z3c.form.interfaces import DISPLAY_MODE


grok.templatedir("templates")


class IProposar(form.Schema):
    """ Enviar missatge als membres /mail_message"""
    form.mode(intro='display')
    intro = TextLine(
        description=_(u"""
            La inclusió de punts nous en l'ordre del dia a iniciativa
            dels membres del Consell de Govern es regula en l'article
            7 del Reglament del Consell de Govern.
            En cas que els membres del Consell de Govern vulguin presentar
            punts nousque no han passat per cap comissió per alguna de les
            raons previstes en l'article, cal emplenar el formulari següent,
            que es tramet automàticament a la Secretaria General. Perquè la
            petició sigui admesa a tràmit, el formulari ha de tenir
            tots els camps emplenats.
            """),
    )
    # 1. Identificaci´o dels membres que presenten la proposta
    form.mode(one='display')

    one = TextLine(
        title=_(u"1. Identificació dels membres que presenten la proposta"),
    )
    numMembres = TextLine(
        title=_(u"Nombre de membres que fan la proposta"),
        required=True)

    nomsMembres = TextLine(
        title=_(u"Nom i cognoms separats amb comes"),
        description=_(u"Cal annexar un document amb el nom i cognom, \
            el DNI i la signatura dels membres que presenten la \
            proposta (informació no pública)"),
        required=True)

    # 2. Identificacio de la persona que fa de ponent
    form.mode(two='display')
    two = TextLine(
        title=_(u"2. Identificació de la persona que fa de ponent")
    )

    nomPonent = TextLine(
        title=_(u"Nom i cognoms"),
        required=False)

    email = TextLine(
        title=_(u"Correu electrònic"),
        required=False)

    tlf = TextLine(
        title=_(u"Telèfon"),
        required=True)

    # 3 Punt de l'ordre del dia que es proposa incloure
    form.mode(three='display')
    three = TextLine(
        title=_(u"3. Punt de l'ordre del dia que es proposa incloure"),
    )

    acord = TextLine(
        title=_(u"Tipus: Acord"),
        required=True)

    puntInfo = TextLine(
        title=_(u"Punt informatiu"),
        required=True)

    title = TextLine(
        title=_(u"Enunciat o títol del punt de l'ordre del dia"),
        required=True)

    justification = TextLine(
        title=_(u"Justificació"),
        required=True)

    text = schema.Text(
        title=_(u"Text que es presenta"),
        required=True)

    # 4 Annexar documents
    file = NamedBlobFile(
        title=_(u"4.  Annexar documents"),
        description=_(u"(màxim 20mb)")
    )


class Message(form.SchemaForm):
    grok.name('proposa_punt_od')
    grok.context(ISessio)
    grok.template("proposarpunt_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True
    schema = IProposar

    def update(self):
        """  Disable the view if username has no roles.
        Send Message if user is Editor / Secretari / Manager """
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

    def updateWidgets(self):
        super(Message, self).updateWidgets()

        session = self.context

        user = api.user.get_current().id

        acl_users = getToolByName(self.context, 'acl_users')
        getLdapUser = acl_users.ldapUPC.acl_users.searchUsers

        try:
            self.widgets["nomPonent"].value = getLdapUser(dn='cn=' + user + ',ou=Users,dc=upc,dc=edu')[0]['sn']
            self.widgets["email"].value = getLdapUser(dn='cn=' + user + ',ou=Users,dc=upc,dc=edu')[0]['mail']
            self.widgets["nomPonent"].mode = DISPLAY_MODE
            self.widgets["email"].mode = DISPLAY_MODE
        except:
            self.widgets["nomPonent"].value = ""
            self.widgets["email"].value = ""

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):

        formData, errors = self.extractData()
        lang = self.context.language
        if 'numMembres' not in formData or 'nomsMembres' not in formData or 'tlf' not in formData or 'title' not in formData or 'justification' not in formData or 'text' not in formData or 'acord' not in formData or 'puntInfo' not in formData:
            if lang == 'ca':
                message = "Falten camps obligatoris: "
            if lang == 'es':
                message = "Faltan campos obligatorios: "
            if lang == 'en':
                message = "Required fields missing: "
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return

        # create propostapunt content
        catalog = getToolByName(self.context, 'portal_catalog')
        f_context = catalog.unrestrictedSearchResults({'portal_type':'Folder', 'id':'puntsproposats'})

        if len(f_context) == 0:
            f_context = _createObjectByType("Folder", self.context, "puntsproposats")
        else:
            f_context = f_context[0].getObject()

        dateAsID = datetime.now().strftime('%d%m%Y%H%M%S')
        proPunt = _createObjectByType("genweb.organs.propostapunt", f_context, dateAsID)

        proPunt.title = formData['title']

        proPunt.text = u"""

        <h3>Justificació</h3>
        <p>%s</p>
        <br>
        <h3>Text proposat</h3>
        <p>%s</p>
        <br>
        <strong>Membres: </strong>%s

        """ % (formData['justification'], formData['text'], formData['nomsMembres'])

        # create annotation with url to propostapunt
        path_to_point = f_context.absolute_url() + "/" + dateAsID
        addPoint(self.context, formData['nomsMembres'], formData['title'], formData['justification'], path_to_point)

        # send mails, we need all the mails from secretaris and editors
        acl_users = getToolByName(self.context, 'acl_users')
        getLdapUser = acl_users.ldapUPC.acl_users.searchUsers
        remitents = ""

        # Sessio
        roles_sessio = self.context.get_local_roles()

        # Organ
        organ = self.context.getParentNode()
        roles_organ = organ.get_local_roles()
        roles = roles_sessio + roles_organ

        # Unitat
        unitat = organ.getParentNode()
        roles_unitat = unitat.get_local_roles()
        roles = roles + roles_unitat

        if roles:
            for (username, roles) in roles:
                try:
                    email = getLdapUser(dn='cn=' + username + ',ou=Users,dc=upc,dc=edu')[0]['mail']
                except:
                    # @llistes.upc.edu o @mylist.upc.edu
                    email = username + "@llistes.upc.edu"
                if 'OG1-Secretari' in roles and email not in remitents:
                    remitents += email + ","
                if 'OG1-Editor' in roles and email not in remitents:
                    remitents += email + ","

        if remitents != "":
            remtents = remitents[:-1]

        # Replace hidden fields to maintain correct urls...
        # body = formData['message'].replace('----@@----http:/', 'http://').replace('----@@----https:/', 'https://').encode('utf-8')

        sender = self.context.aq_parent.fromMail
        body = u"<p>Hi ha una nova proposta de punt a la sessió %s,\
        es pot veure al següent enllaç: <a href=%s>%s</a></p><br/>\
        " % (self.context.title, path_to_point, formData['title'])

        body_r = u"<p>La teva proposta per un nou punt d'ordre (%s) \
        a la sessió %s, ha sigut enviat correctament!\
        " % (formData['title'], self.context.title)

        try:
            # Mail to secretaris and editors
            self.context.MailHost.send(
                body,
                mto=remitents,  # email de tots els secretaris i editors
                mfrom=sender,
                subject="Nova proposta de punt",
                encode=None,
                immediate=True,
                charset='utf8',
                msg_type='text/html')

            # Mail to sender, to confirm
            self.context.MailHost.send(
                body_r,
                mto=self.widgets["email"].value or formData['email'],  # email del membre ponent
                mfrom=sender,
                subject="Proposta punt enviada correctament",
                encode=None,
                immediate=True,
                charset='utf8',
                msg_type='text/html')

            self.context.plone_utils.addPortalMessage(
                _("Proposta creada i missatge enviat correctament"), 'info')

        except:
            self.context.plone_utils.addPortalMessage(
                _("Proposta i missatge no enviat. Comprovi els camps"), 'error')

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
