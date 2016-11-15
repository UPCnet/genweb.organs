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
            message = 'Falten camps obligatoris'
            if lang == 'es':
                message = "Faltan campos obligatorios"
            if lang == 'en':
                message = "Required fields missing"
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
            lines = text.splitlines()
            last_generated_id = None
            last_generated_subid = None
            tab = 0



            # llista  = []
            # dic = {}
            # for line in lines:
            #     if line.startswith(' '):

            #         # get previous id
            #         if last_generated_id:
            #             obj = api.content.create(
            #                 type='genweb.organs.punt',
            #                 title=line.lstrip().rstrip(),
            #                 container=self.context)

            #             if tab is '1':
            #                 obj.proposalPoint = str(last_generated_id) + '.' + str(int(tab))
            #                 tab = tab + 1
            #     else:
            #         if dic is not None:
            #             llista.append(dic)
            #             dic = {}

            #         item_id = len(self.context.items()) + 1

            #         obj = api.content.create(
            #             type='genweb.organs.punt',
            #             title=line.rstrip(),
            #             container=self.context)

            #         obj.proposalPoint = item_id
            #         last_generated_id = item_id


    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
