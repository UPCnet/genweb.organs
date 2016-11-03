# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from plone import api
from genweb.organs import _
from zope.container.interfaces import INameChooser


class changeTitle(BrowserView):

    def __call__(self):
        """ Adding log info when renaming content """
        annotations = IAnnotations(self.context)
        if annotations is not None:
            origin_path = '/'.join(self.context.getPhysicalPath()) + '/' + self.request.form['pk']
            print origin_path
            newvalue = self.request.form['value']

            KEY = 'genweb.organs.logMail'
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
                username = 'Anonymous user'
            values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
                          message=_("Rename Title"),
                          fromMail=username,
                          toMail=origin_path + ' -> ' + newvalue)

            try:
                entry = api.content.find(path=origin_path, depth=0)[0]
                old_id = entry.id
                container = entry.getObject().aq_parent
                chooser = INameChooser(container)
                new_id = chooser.chooseName(newvalue, entry.getObject())
                container.manage_renameObject(old_id, new_id)
                newObject = api.content.find(id=new_id, path=container.absolute_url_path())[0]
                newObject.getObject().title = newvalue
                newObject.getObject().reindexObject()

                # Correct transaction, then  -> save the process log
                data.append(values)
                annotations[KEY] = data
            except:
                pass
