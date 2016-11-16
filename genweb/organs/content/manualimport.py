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
from collections import defaultdict
import re

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
            # nodes = []

            content = text.splitlines()
            # for line in content:
            #     for node in line.split(','):
            #         nodes.append(node.rstrip().lstrip())

            # bTree = defaultdict(list)
            # for father, children in zip(nodes[0::2], nodes[0::2]):
            #     print 'Inserting (' + father + ', ' + children + ')'
            #     bTree[father].append(children)
            # print(bTree)

            # depth = 0
            # root = {"punt": "root", "subpunt": []}
            # parents = []
            # node = root
            # for line in content:
            #     line = line.rstrip()
            #     # import ipdb;ipdb.set_trace()
            #     newDepth = re.search('\S', line).start() +1

            #     print newDepth, line
            #     # if the new depth is shallower than previous, we need to remove items from the list
            #     if newDepth < depth:
            #         parents = parents[:newDepth]
            #     # if the new depth is deeper, we need to add our previous node
            #     elif newDepth == depth + 1:
            #         parents.append(node)
            #     # levels skipped, not possible
            #     # elif newDepth > depth + 1:
            #     #     raise Exception("Invalid file")
            #     depth = newDepth

            #     # create the new node
            #     node = {"punt": line.strip(), "subpunt":[]}
            #     # add the new node into its parent's children
            #     parents[-1]["subpunt"].append(node)

            # json_list = root["subpunt"]
            # print json_list

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
