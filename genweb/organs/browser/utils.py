# -*- coding: utf-8 -*-
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from genweb.organs.interfaces import IGenwebOrgansLayer
import json
import transaction
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.content.sessio import ISessio
from plone.namedfile.file import NamedBlobFile


class changeMigrated(grok.View):
    # Change migrated property of sessions.
    # No se pueden editar sessiones de la versión antigua, pero
    # en algunos casos, nos han pedido que se pueda...
    # Este código cambia el valor de la propiedad para eso
    grok.context(IDexterityContent)
    grok.name('change_migrated_to')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        # http:/session_url/change_migrated_to?value=False
        messages = IStatusMessage(self.request)
        if self.context.portal_type == 'genweb.organs.sessio':
            if self.request['value'] == 'True':
                elements = api.content.find(path=self.context.absolute_url_path())
                for item in elements:
                    value = item.getObject()
                    value.migrated = True
                    transaction.commit()
            elif self.request['value'] == 'False':
                elements = api.content.find(path=self.context.absolute_url_path())
                for item in elements:
                    value = item.getObject()
                    value.migrated = False
                    transaction.commit()
            else:
                return

            messages.add('migrated property set to: ' + str(self.request['value']), type='warning')
            self.request.response.redirect(self.context.absolute_url())
        else:
            pass


class changeInitialProposalPoint(grok.View):
    # After migration, there was an error...
    # Point 0 must be Informat, instead of Aprovat
    grok.context(IDexterityContent)
    grok.name('change_proposal_after_migration')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        items = api.content.find(path='/', portal_type='genweb.organs.punt')
        results = []
        for item in items:
            value = item.getObject()
            if value.proposalPoint is '0':
                value.estatsLlista = 'Informat'
                results.append(dict(title=item.Title,
                                    path=item.getURL(),
                                    proposalPoint=value.proposalPoint,
                                    estat=value.estatsLlista))
        return json.dumps(results)


class changeMimeType(grok.View):
    # After migration, there was an error...
    # Incorrect mimetypes in some pdf files
    # application/force-download -->
    # application/x-download -->
    # application/x-octet-stream -->

    grok.context(IDexterityContent)
    grok.name('change_file_mimetype_to_pdf')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        files = api.content.find(path='/', portal_type='genweb.organs.file')
        results = []
        oldvisible = newvisible = oldhidden = newhidden = ''
        types = ['application/force-download', 'application/x-download', 'application/x-octet-stream']
        for file in files:
            changed = False
            item = file.getObject()
            if item.visiblefile and item.hiddenfile:
                oldvisible = item.visiblefile.contentType
                oldhidden = item.hiddenfile.contentType
                if item.visiblefile.contentType in types:
                    item.visiblefile.contentType = 'application/pdf'
                    newvisible = item.visiblefile.contentType
                    changed = True
                    transaction.commit()

                if item.hiddenfile.contentType in types:
                    item.hiddenfile.contentType = 'application/pdf'
                    newhidden = item.hiddenfile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))
            elif item.hiddenfile:
                oldvisible = newvisible = ''
                oldhidden = item.hiddenfile.contentType
                if item.hiddenfile.contentType in types:
                    item.hiddenfile.contentType = 'application/pdf'
                    newhidden = item.hiddenfile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))

            elif item.visiblefile:
                oldvisible = item.visiblefile.contentType
                oldhidden = newhidden = ''
                if item.visiblefile.contentType in types:
                    item.visiblefile.contentType = 'application/pdf'
                    newvisible = item.visiblefile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))

        return json.dumps(results)


class listpermissions(grok.View):
    # List of permissions in object, in json format

    grok.context(IDexterityContent)
    grok.name('permissions_in_og_folders')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        all_brains = api.content.find(portal_type='genweb.organs.organgovern')
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            roles = obj.get_local_roles()
            secretaris = []
            editors = []
            membres = []
            afectats = []
            if roles:
                for (username, role) in roles:
                    if 'OG1-Secretari' in role:
                        secretaris.append(str(username))
                    if 'OG2-Editor' in role:
                        editors.append(str(username))
                    if 'OG3-Membre' in role:
                        membres.append(str(username))
                    if 'OG4-Afectat' in role:
                        afectats.append(str(username))
            element = {
                'title': obj.Title(),
                'path': obj.absolute_url() + '/sharing',
                'OG1-Secretari': secretaris,
                'OG2-Editor': editors,
                'OG3-Membre': membres,
                'OG4-Afectat': afectats,
                'organType': obj.organType,
                'fromMail': obj.fromMail,
                'adrecaLlista': obj.adrecaLlista,
                'acronim': obj.acronim
            }

            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)


class MovePublicfilestoPrivate(grok.View):
    # After migrating data, some files came with an error.
    # They were located as public files, but must be Private.
    # This view change all files from public to private and viceversa
    # in a given session

    grok.context(ISessio)
    grok.name('movefilestoprivateorpublic')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def showfiles(self):
        path = '/'.join(self.context.getPhysicalPath())
        all_brains = api.content.find(portal_type='genweb.organs.file', path=path)
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            if obj.visiblefile:
                visible = obj.visiblefile.filename
            else:
                visible = 'Empty'
            if obj.hiddenfile:
                hidden = obj.hiddenfile.filename
            else:
                hidden = 'Empty'
            element = {
                'visiblefile': visible,
                'hiddenfile': hidden,
                'path': obj.absolute_url()
            }

            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)

    def movetoPrivate(self):
        path = '/'.join(self.context.getPhysicalPath())
        all_brains = api.content.find(portal_type='genweb.organs.file', path=path)
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            # Show initial values
            if getattr(obj, 'visiblefile', False):
                initial_visible = obj.visiblefile.filename
            else:
                initial_visible = 'Empty'
            if getattr(obj, 'hiddenfile', False):
                initial_hidden = obj.hiddenfile.filename
            else:
                initial_hidden = 'Empty'
            final_visible = 'Not modified'
            final_hidden = 'Not modified'
            if not obj.hiddenfile and obj.visiblefile:
                initial_visible = obj.visiblefile.filename
                initial_hidden = 'Empty'
                # Move public to private
                obj.hiddenfile = NamedBlobFile(
                    data=obj.visiblefile.data,
                    contentType=obj.visiblefile.contentType,
                    filename=obj.visiblefile.filename
                )
                transaction.commit()
                del obj.visiblefile
                final_visible = 'Empty (Deleted)'
                final_hidden = obj.hiddenfile.filename
            element = {
                'original-visiblefile': initial_visible,
                'original-hiddenfile': initial_hidden,
                'path': obj.absolute_url(),
                'final-visiblefile': final_visible,
                'final-hiddenfile': final_hidden,
            }
            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)

    def movetoPublic(self):
        path = '/'.join(self.context.getPhysicalPath())
        all_brains = api.content.find(portal_type='genweb.organs.file', path=path)
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            # Show initial values
            if getattr(obj, 'visiblefile', False):
                initial_visible = obj.visiblefile.filename
            else:
                initial_visible = 'Empty'
            if getattr(obj, 'hiddenfile', False):
                initial_hidden = obj.hiddenfile.filename
            else:
                initial_hidden = 'Empty'
            final_visible = 'Not modified'
            final_hidden = 'Not modified'
            if obj.hiddenfile and not obj.visiblefile:
                initial_visible = 'Empty'
                initial_hidden = obj.hiddenfile.filename
                # Move private to public
                obj.visiblefile = NamedBlobFile(
                    data=obj.hiddenfile.data,
                    contentType=obj.hiddenfile.contentType,
                    filename=obj.hiddenfile.filename
                )
                transaction.commit()
                del obj.hiddenfile
                final_visible = obj.visiblefile.filename
                final_hidden = 'Empty (Deleted)'
            element = {
                'original-visiblefile': initial_visible,
                'original-hiddenfile': initial_hidden,
                'path': obj.absolute_url(),
                'final-visiblefile': final_visible,
                'final-hiddenfile': final_hidden,
            }
            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)

    def render(self):
        """ Execute /movefilestoprivateorpublic """
        if 'showfiles' in self.request.form:
            return self.showfiles()
        if 'move2Private' in self.request.form:
            return self.movetoPrivate()
        if 'move2Public' in self.request.form:
            return self.movetoPublic()

        return 'DANGER: This code moves files from public to private and viceversa. <br/>\
        <br/>usage: /movefilestoprivateorpublic?  <b><a href="?showfiles">showfiles</a></b>\
         | <b><a href="?move2Private">move2Private</a></b> \
         | <b><a href="?move2Public">move2Public</a></b>'


class showColorOrgans(grok.View):

    grok.context(IDexterityContent)
    grok.name('showColorOrgans')
    grok.require('cmf.ManagePortal')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        path = '/'.join(self.context.getPhysicalPath())
        all_brains = api.content.find(portal_type='genweb.organs.organgovern', path=path)
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            element = {
                'color': obj.eventsColor,
                'path': obj.absolute_url() + '/edit'
            }

            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)
