# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from genweb.organs.interfaces import IGenwebOrgansLayer
import json
import transaction
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.content.sessio.sessio import ISessio
from plone.namedfile.file import NamedBlobFile
from zope.interface import Interface
import requests
from plone.namedfile.file import NamedBlobImage
from plone.app.textfield.value import RichTextValue
from datetime import datetime
from plone.event.interfaces import IEventAccessor
import os
import pytz
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from Products.Five.browser import BrowserView


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def getLoremIpsum(number, length, type_code):
    """ Returns a RichTextValue with lorem ipsum text """
    if os.environ.get("PLONE_TESTING"):
        text = "Lorem ipsum test"
    else:
        text = requests.get(
            f"http://loripsum.net/api/{number}/{type_code}/{length}",
            verify=False,
            timeout=10
        ).text  # usamos .text para obtener str

    return RichTextValue(text, 'text/plain', 'text/html')


def getRandomImage(w, h):
    """ Returns dummy image """
    data = requests.get(
        'http://dummyimage.com/{0}x{1}/aeaeae/ffffff'.format(w, h),
        verify=False, timeout=10).content
    return NamedBlobImage(data=data,
                          filename=u'image.jpg',
                          contentType='image/jpeg')


def create_organ_content(og_unit, og_type, og_string, og_title, og_id):
    """ Creates all structure based on organ type """
    open_og = api.content.create(
        type='genweb.organs.organgovern',
        title=og_title,
        id=og_id,
        container=og_unit,
        safe_id=True)
    open_og.acronim = og_string
    open_og.descripcioOrgan = getLoremIpsum(1, 'medium', 'plaintext')
    open_og.fromMail = 'testing@ploneteam.upcnet.es'
    open_og.organType = og_type
    open_og.logoOrgan = getRandomImage(200, 200)
    open_og.visiblefields = True
    open_og.eventsColor = 'green'
    open_og.membresOrgan = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    open_og.convidatsPermanentsOrgan = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    open_og.adrecaLlista = 'membresconvidats@ploneteam.upcnet.es'
    session_open = api.content.create(
        type='genweb.organs.sessio',
        id='planificada',
        title='Sessió Planificada',
        container=open_og,
        safe_id=True)
    session_open.membresConvocats = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    session_open.membresConvidats = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    session_open.llistaExcusats = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    session_open.assistents = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    session_open.noAssistents = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    session_open.adrecaLlista = 'convidats@ploneteam.upcnet.es'
    session_open.llocConvocatoria = 'Barcelona'
    session_open.numSessio = '01'
    acc = IEventAccessor(session_open)
    tz = pytz.timezone("Europe/Vienna")
    acc.start = tz.localize(datetime(2018, 11, 18, 10, 0))
    acc.end = tz.localize(datetime(2018, 11, 20, 10, 0))
    acc.timezone = "Europe/Vienna"
    punt = api.content.create(
        type='genweb.organs.punt',
        id='punt',
        title='Punt Exemple',
        container=session_open)
    punt.proposalPoint = 1
    punt.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    punt.estatsLlista = u'Esborrany'
    # For working test code. If not added, Plone works, but test dont.
    constraints = ISelectableConstrainTypes(punt)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(
        ('genweb.organs.subpunt', 'genweb.organs.acord', 'genweb.organs.file',
         'genweb.organs.document'))
    document_public = api.content.create(
        type='genweb.organs.document',
        id='docpublic',
        title='Document contingut public',
        container=punt)
    document_public.description = u"Lorem Ipsum description"
    document_public.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    document_restringit = api.content.create(
        type='genweb.organs.document',
        id='docrestringit',
        title='Document contingut restringit',
        container=punt)
    document_restringit.description = u"Lorem Ipsum description"
    document_restringit.alternateContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    document_both = api.content.create(
        type='genweb.organs.document',
        id='docboth',
        title='Document contingut public i restringit',
        container=punt)
    document_both.description = u"Lorem Ipsum description"
    document_both.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    document_both.alternateContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    # For working tests code
    # constraints = ISelectableConstrainTypes(punt)
    # constraints.setConstrainTypesMode(1)
    # constraints.setLocallyAllowedTypes(('genweb.organs.subpunt', 'genweb.organs.acord', 'genweb.organs.file', 'genweb.organs.document'))
    subpunt = api.content.create(
        type='genweb.organs.subpunt',
        id='subpunt',
        title='SubPunt Exemple',
        container=punt)
    subpunt.proposalPoint = 1.1
    subpunt.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    subpunt.estatsLlista = u'Esborrany'
    subacord = api.content.create(
        type='genweb.organs.acord',
        id='acord',
        title='Acord Exemple',
        container=punt)
    subacord.proposalPoint = '2'
    subacord.agreement = og_string + '/2018/01/02'
    subacord.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    subacord.estatsLlista = u'Esborrany'
    acord = api.content.create(
        type='genweb.organs.acord',
        id='acord',
        title='Acord Exemple',
        container=session_open)
    acord.proposalPoint = '2'
    acord.agreement = og_string + '/2018/01/01'
    acord.defaultContent = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    acord.estatsLlista = u'Esborrany'
    api.content.copy(source=document_public, target=acord, safe_id=True)
    api.content.copy(source=document_restringit, target=acord, safe_id=True)
    api.content.copy(source=document_both, target=acord, safe_id=True)
    api.content.copy(source=document_public, target=subpunt, safe_id=True)
    api.content.copy(source=document_restringit, target=subpunt, safe_id=True)
    api.content.copy(source=document_both, target=subpunt, safe_id=True)
    api.content.copy(source=document_public, target=subacord, safe_id=True)
    api.content.copy(source=document_restringit, target=subacord, safe_id=True)
    api.content.copy(source=document_both, target=subacord, safe_id=True)
    pdf_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..', 'tests')) + '/testfile.pdf'

    with open(pdf_file, 'rb') as f:
        pdf_data = f.read()

    public_file = NamedBlobFile(
        data=pdf_data,
        contentType='application/pdf',
        filename=u'pdf-public.pdf'
    )

    restricted_file = NamedBlobFile(
        data=pdf_data,
        contentType='application/pdf',
        filename=u'pdf-restringit.pdf'
    )
    acta = api.content.create(
        type='genweb.organs.acta',
        id='acta',
        title='Acta Exemple',
        container=session_open)
    acta.llocConvocatoria = u'Barcelona'
    acta.enllacVideo = u'http://www.upc.edu'
    acta.ordenDelDia = RichTextValue(
        getLoremIpsum(2, 'long', 'html'),
        'text/html', 'text/html').output
    acta.membresConvocats = acta.ordenDelDia
    acta.membresConvidats = acta.ordenDelDia
    acta.llistaExcusats = acta.ordenDelDia
    acta.llistaNoAssistens = acta.ordenDelDia
    acta.file = public_file
    acta.horaInici = session_open.start
    acta.horaFi = session_open.end
    acc.horaFi = tz.localize(datetime(2018, 11, 20, 10, 0))
    audio = api.content.create(
        type='genweb.organs.audio',
        id='audio',
        title='Audio Exemple',
        container=acta)
    audio.description = u'audio mp3 description'
    mp3_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..', 'tests')) + '/testaudio.mp3'

    with open(mp3_file, 'rb') as f:
        mp3_data = f.read()

    audio_file = NamedBlobFile(
        data=mp3_data,
        contentType='audio/mpeg',
        filename=u'audio.mp3'
    )
    audio.file = audio_file

    filepunt_1 = api.content.create(
        type='genweb.organs.file',
        id='public',
        title='Fitxer NOMÉS Públic',
        container=punt)
    filepunt_1.visiblefile = public_file
    filepunt_2 = api.content.create(
        type='genweb.organs.file',
        id='restringit',
        title='Fitxer NOMÉS Restringit',
        container=punt)
    filepunt_2.hiddenfile = restricted_file
    filepunt_3 = api.content.create(
        type='genweb.organs.file',
        id='public-restringit',
        title='Fitxer Públic i Restringit',
        container=punt)
    filepunt_3.visiblefile = public_file
    filepunt_3.hiddenfile = restricted_file
    api.content.copy(source=filepunt_1, target=subpunt, safe_id=True)
    api.content.copy(source=filepunt_2, target=subpunt, safe_id=True)
    api.content.copy(source=filepunt_3, target=subpunt, safe_id=True)
    api.content.copy(source=filepunt_1, target=acord, safe_id=True)
    api.content.copy(source=filepunt_2, target=acord, safe_id=True)
    api.content.copy(source=filepunt_3, target=acord, safe_id=True)
    api.content.copy(source=filepunt_1, target=subacord, safe_id=True)
    api.content.copy(source=filepunt_2, target=subacord, safe_id=True)
    api.content.copy(source=filepunt_3, target=subacord, safe_id=True)

    sessio_convocada = api.content.copy(
        source=session_open, target=open_og, id='convocada')
    sessio_convocada.title = 'Sessió Convocada'
    api.content.transition(obj=sessio_convocada, transition='convocar')
    transaction.commit()

    sessio_realitzada = api.content.copy(
        source=sessio_convocada, target=open_og, id='realitzada')
    sessio_realitzada.title = 'Sessió Realitzada'
    api.content.transition(obj=sessio_realitzada, transition='convocar')
    api.content.transition(obj=sessio_realitzada, transition='realitzar')
    transaction.commit()

    sessio_tancada = api.content.copy(
        source=sessio_realitzada, target=open_og, id='tancada')
    sessio_tancada.title = 'Sessió Tancada'
    api.content.transition(obj=sessio_tancada, transition='convocar')
    api.content.transition(obj=sessio_tancada, transition='realitzar')
    api.content.transition(obj=sessio_tancada, transition='tancar')
    transaction.commit()

    sessio_modificada = api.content.copy(
        source=sessio_realitzada, target=open_og, id='correccio')
    sessio_modificada.title = 'Sessió en Correcció'
    api.content.transition(obj=sessio_modificada, transition='convocar')
    api.content.transition(obj=sessio_modificada, transition='realitzar')
    api.content.transition(obj=sessio_modificada, transition='tancar')
    api.content.transition(obj=sessio_modificada, transition='corregir')
    transaction.commit()


class changeMigrated(BrowserView):
    # Change migrated property of sessions.
    # No se pueden editar sessiones de la versión antigua, pero
    # en algunos casos, nos han pedido que se pueda...
    # Este código cambia el valor de la propiedad para eso
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

            messages.add(
                'migrated property set to: ' + str(self.request['value']),
                type='warning')
            self.request.response.redirect(self.context.absolute_url())
        else:
            pass


class changeInitialProposalPoint(BrowserView):
    # After migration, there was an error...
    # Point 0 must be Informat, instead of Aprovat
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


class changeMimeType(BrowserView):
    # After migration, there was an error...
    # Incorrect mimetypes in some pdf files
    # application/force-download -->
    # application/x-download -->
    # application/x-octet-stream -->

    def render(self):
        files = api.content.find(path='/', portal_type='genweb.organs.file')
        results = []
        oldvisible = newvisible = oldhidden = newhidden = ''
        types = ['application/force-download',
                 'application/x-download', 'application/x-octet-stream']
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


class listpermissions(BrowserView):
    # List of permissions in object, in json format

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


class MovePublicfilestoPrivate(BrowserView):
    # After migrating data, some files came with an error.
    # They were located as public files, but must be Private.
    # This view change all files from public to private and viceversa
    # in a given session

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


class showColorOrgans(BrowserView):
    # Registrar en ZCML: name='showColorOrgans', for='plone.dexterity.interfaces.IDexterityContent', permission='cmf.ManagePortal', layer='genweb.organs.interfaces.IGenwebOrgansLayer'
    def render(self):
        path = '/'.join(self.context.getPhysicalPath())
        all_brains = api.content.find(
            portal_type='genweb.organs.organgovern', path=path)
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            element = {
                'color': obj.eventsColor,
                'path': obj.absolute_url() + '/edit',
                'sessions_visible_in_public_calendar': obj.visiblefields
            }

            results.append(element)
        return json.dumps(results, indent=2, sort_keys=True)


class createTestContent(BrowserView):
    # Este código crea contenido de prueba para hacer TEST de acceso y checking de permisos
    def render(self):
        print("## Executed create_test_content view to create testingfolder content...")
        messages = IStatusMessage(self.request)
        portal = api.portal.get()
        try:
            api.content.delete(
                obj=portal['ca']['testingfolder'],
                check_linkintegrity=False)
        except:
            pass

        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=portal['ca'])

        create_organ_content(og_unit, 'open_organ', 'OG.OPEN',
                             'Organ TEST Obert', 'obert')
        # create_organ_content(og_unit, 'restricted_to_affected_organ', 'OG.AFFECTED', 'Organ TEST restringit a AFECTATS', 'afectats')
        # create_organ_content(og_unit, 'restricted_to_members_organ', 'OG.MEMBERS', 'Organ TEST restringit a MEMBRES', 'membres')

        messages.add(
            'Created testingfolder with TEST content to check permissions.',
            type='warning')
        self.request.response.redirect(self.context.absolute_url())


class testFilesAccess(BrowserView):
    # Este código prueba los permisos de acceso a los ficheros de organs
    def render(self):
        messages = IStatusMessage(self.request)
        portal = api.portal.get()
        try:
            testfolder = portal['ca']['testingfolder']
            api.content.find(
                context=testfolder,
                depth=0)[0]
        except:
            return "You must create default content with /create_test_content"

        # Create a new user.
        try:
            api.user.create(
                username="testuser",
                roles=('Anonymous',),
                email="anonuser@test.com",
            )
        except:
            pass

        # with api.env.adopt_user(username="testuser"):
            # import ipdb; ipdb.set_trace()
            # api.user.grant_roles(username="testuser", roles=['OG1-Secretari'])
            # portal.ca.testingfolder.obert.planificada.punt.public.restrictedTraverse('@@view')()
            # print portal.ca.testingfolder.obert.planificada.punt.public.restrictedTraverse('@@view')()
            # api.user.grant_roles(username="testuser", roles=['OG2-Editor'])
            # portal.ca.testingfolder.obert.planificada.punt.public.restrictedTraverse('@@view')()
            # print portal.ca.testingfolder.obert.planificada.punt.public.restrictedTraverse('@@view')()

        api.user.delete(username='testuser')
        return "End of tests..."

        messages.add('TESTED FILE PERMISSIONS.', type='warning')
        # self.request.response.redirect(self.context.absolute_url())
