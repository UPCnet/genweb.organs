# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from five import grok
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.directives import form
from z3c.form import button
from zope import schema

from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs.utils import addEntryLog
from genweb.organs import utils

import transaction
import unicodedata

grok.templatedir("templates")


class IMessage(form.Schema):
    """ Modal used to create massive punts: /manualStructureCreation
    """

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Manual Import"),
        description=_("Add content separated by -- and they will by added as Agreements."),
        required=False,
    )


class Message(form.SchemaForm):
    grok.name('manualStructureCreation')
    grok.context(ISessio)
    grok.template("manualimport_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True

    schema = IMessage

    # This trick hides the editable border and tabs in Plone
    def update(self):
        """ Return true if user is Editor or Manager, but if the session """
        """ came from the previous version, then make impossible to """
        """ create new elements """
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property:
            if self.context.migrated is True:
                raise Unauthorized

        try:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized
        except:
            raise Unauthorized

    def updateWidgets(self):
        super(Message, self).updateWidgets()

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):
        """ Send the email to the configured mail address
            in properties and redirect to the
            front page, showing a status message to say
            the message was received. """
        formData, errors = self.extractData()
        lang = self.context.language
        if formData['message'] is None:
            message = 'Falten els valors dels punts. Cap canvi realitzat.'
            if lang == 'es':
                message = "Faltan los valores de los puntos. No se ha realizado ningún cambio."
            if lang == 'en':
                message = "Required values missing. No changes made."
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return self.request.response.redirect(self.context.absolute_url())

        """ Adding message information to context in annotation format """
        addEntryLog(self.context, None, _(u'Massive agreements imported'), '')

        # Creating new objects
        text = formData['message']

        values = self.aq_parent.aq_parent.estatsLlista
        value = values.split('</p>')[0]
        item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
        defaultEstat = ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8')

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        puntsInFolder = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        index = len(puntsInFolder) + 1

        content = text.splitlines()
        subindex = 0
        previousPuntContainer = None
        errors = None
        for line in content:
            if len(line) == 0:
                continue
            else:
                if line.startswith((' ', '\t')) is False:
                    # No hi ha blanks, es un punt o un acord
                    # Obtenim una A o un P per saber si es Acord o Punt
                    portal_type = line.lstrip().rstrip().split(' ')[0].upper()
                    if str(portal_type) == 'A':  # Es tracta d'un acord
                        line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.acord',
                                title=line,
                                container=self.context)
                    elif str(portal_type) == 'P':  # Es tracta d'un punt
                        line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.punt',
                                title=line,
                                container=self.context)
                    else:  # Supossem que per defecte sense espais es un Punt
                        line = line.lstrip().rstrip()
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.punt',
                                title=line,
                                container=self.context)
                    obj.proposalPoint = unicode(str(index))
                    obj.estatsLlista = defaultEstat
                    index = index + 1
                    subindex = 1
                    previousPuntContainer = obj
                    obj.reindexObject()
                else:
                    # hi ha blanks, es un subpunt o un acord
                    portal_type = line.lstrip().rstrip().split(' ')[0].upper()
                    if previousPuntContainer.portal_type == 'genweb.organs.punt':
                        if str(portal_type) == 'A':  # Es tracta d'un acord
                            line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.acord',
                                    title=line,
                                    container=previousPuntContainer)
                        elif str(portal_type) == 'P':  # Es tracta d'un punt
                            line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.subpunt',
                                    title=line,
                                    container=previousPuntContainer)
                        else:  # Supossem que per defecte sense espais es un Punt
                            line = line.lstrip().rstrip()
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.subpunt',
                                    title=line,
                                    container=previousPuntContainer)

                        newobj.proposalPoint = unicode(str(index - 1) + str('.') + str(subindex))
                        newobj.estatsLlista = defaultEstat
                        newobj.reindexObject()
                        subindex = subindex + 1
                    else:
                        # dintre d'un acord no podem crear res...
                        errors = _(u"No s'han creat tot els elements perque no segueixen la norma. Dintre d'un Acord no es pot afeigr res.")
                        subindex = subindex - 1

        transaction.commit()

        if errors:
            IStatusMessage(self.request).addStatusMessage(errors, type="error")
            return self.request.response.redirect(self.context.absolute_url())
        else:
            message = "S'han creats els punts indicats."
            if lang == 'es':
                message = "Se han creado los puntos indicados."
            if lang == 'en':
                message = "Indicated fields have been created."
            IStatusMessage(self.request).addStatusMessage(message, type="success")
            return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
