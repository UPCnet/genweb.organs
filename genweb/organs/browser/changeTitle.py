# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from plone import api
from genweb.organs import _
from zope.container.interfaces import INameChooser
from genweb.organs.utils import addEntryLog


class changeTitle(BrowserView):

    def __call__(self):
        """ Adding log info when renaming content """
        annotations = IAnnotations(self.context)
        if annotations is not None:
            # http://localhost:8080/Plone/ca/consell-de-direccio/organ1/sess/changeTitle?pk=OLD_ID&name=&value=NEW_ID
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
                container.manage_renameObject(old_id, new_id)

                newObject = api.content.find(id=new_id, path='/'.join(origin_path.split('/')[:-1]))[0]
                newObject.getObject().title = newvalue
                newObject.getObject().reindexObject()

                # ok transaction, then  -> save the process log
                recipients = origin_path + ' -> ' + newvalue
                addEntryLog(self.context, None, _(u"Change Agreement"), recipients)
            except:
                pass
