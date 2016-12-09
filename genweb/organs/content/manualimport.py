# -*- coding: utf-8 -*-
from plone import api
from five import grok
from datetime import datetime
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from zope.annotation.interfaces import IAnnotations
from AccessControl import Unauthorized
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from Products.CMFCore.utils import getToolByName
import transaction


grok.templatedir("templates")


class IMessage(form.Schema):
    """ Define the fields of this form
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

    # fields = field.Fields(IMessage)

    # This trick hides the editable border and tabs in Plone
    def update(self):
        """ Return true if user is Editor or Manager """
        try:
            username = api.user.get_current().getId()
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Editor' in roles or 'Manager' in roles:
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

        """ Adding message information to context in annotation format
        """
        KEY = 'genweb.organs.logMail'
        annotations = IAnnotations(self.context)

        if annotations is not None:
            logData = annotations.get(KEY, None)
            try:
                len(logData)
                # Get data and append values
                data = annotations.get(KEY)
            except:
                # If it's empty, initialize data
                data = []
            dateMail = datetime.now()

            anon = api.user.is_anonymous()
            if not anon:
                username = api.user.get_current().id
            else:
                username = ''
            toMail = ''
            values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
                          message=_("Massive agreements imported"),
                          fromMail=username,
                          toMail=toMail)

            data.append(values)
            annotations[KEY] = data

            # Creating new objects

            text = formData['message']
            defaultEstat = str(self.aq_parent.aq_parent.estatsLlista.split('<br />')[0].replace('<p>','').replace('</p>','').split('#')[0].rsplit(' ')[0])
            portal_catalog = getToolByName(self, 'portal_catalog')
            folder_path = '/'.join(self.context.getPhysicalPath())
            puntsInFolder = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})
            index = len(puntsInFolder) + 1

            content = text.splitlines()
            subindex = 0
            previousPuntContainer = None
            for line in content:
                if line.startswith((' ', '\t')) is False:
                    # No hi ha blanks, es un punt
                    line = line.lstrip().rstrip()  # esborrem tots els blanks
                    obj = api.content.create(
                        type='genweb.organs.punt',
                        title=line,
                        container=self.context)
                    obj.proposalPoint = unicode(str(index))
                    obj.estatsLlista = defaultEstat
                    index = index + 1
                    subindex = 1
                    previousPuntContainer = obj
                    transaction.commit()
                else:
                    # starts with blanks, es un subpunt
                    line = line.lstrip().rstrip()  # esborrem tots els blanks
                    obj = api.content.create(
                        type='genweb.organs.subpunt',
                        title=line,
                        container=previousPuntContainer)
                    # TODO: Optimize previous line! runs slower!

                    obj.proposalPoint = unicode(str(index-1) + str('.') + str(subindex))
                    obj.estatsLlista = defaultEstat
                    subindex = subindex + 1

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
