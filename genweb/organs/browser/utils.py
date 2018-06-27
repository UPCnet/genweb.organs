# -*- coding: utf-8 -*-
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from genweb.organs.interfaces import IGenwebOrgansLayer
import json
import transaction
from Products.statusmessages.interfaces import IStatusMessage


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
