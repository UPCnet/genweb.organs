# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from genweb.organs import _
from zope.container.interfaces import INameChooser
from genweb.organs.utils import addEntryLog


class changeTitle(BrowserView):
    """ Change the title of the element """

    def __call__(self):
        # http://localhost:8080/Plone/ca/eetac/organ/session/changeTitle?pk=OLD_ID&name=&value=NEW_ID
        try:
            origin_path = '/'.join(self.context.getPhysicalPath()) + '/' + self.request.form['pk']
            newvalue = self.request.form['value']
        except:
            return None

        try:
            entry = api.content.find(path=origin_path, depth=0)[0]
            old_id = entry.id
            container = entry.getObject().aq_parent
            chooser = INameChooser(container)
            new_id = chooser.chooseName(newvalue, entry.getObject())
            with api.env.adopt_roles(['OG1-Secretari']):
                container.manage_renameObject(old_id, new_id)

            newObject = api.content.find(id=new_id, path='/'.join(origin_path.split('/')[:-1]))[0]
            newObject.getObject().title = newvalue
            newObject.getObject().reindexObject()

            # transaction ok, then write log
            recipients = origin_path + ' -> ' + newvalue
            addEntryLog(self.context, None, _(u"Changed Title"), recipients)
            # This line is only to bypass the CSRF WARNING
            # WARNING plone.protect error parsing dom, failure to add csrf token to response for url ...
            return "Changed Title"
        except:
            pass
