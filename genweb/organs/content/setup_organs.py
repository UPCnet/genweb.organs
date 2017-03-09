# -*- coding: utf-8 -*-
from plone import api
from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot
from cgi import parse_qs
import transaction
from datetime import datetime
from plone.app.event.dx.behaviors import data_postprocessing
from datetime import timedelta
from plone.app.event.dx.behaviors import IEventBasic

grok.templatedir("templates")

import pytz
tz = pytz.timezone('Europe/Madrid')


class setup(grok.View):
    grok.name('setup_organs')
    grok.template('setup_organs')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def update(self):
        base_url = "%s/@@setup_organs" % str(self.context.absolute_url_path())
        qs = self.request.get('QUERY_STRING', None)

        if qs is not None:
            query = parse_qs(qs)
            if 'create' in query:
                self.createContent()
                self.request.response.redirect(base_url)

    def contentStatus(self):
        objects = [(u'ORGANS', [('organs', 'ca'), ('organos', 'es'), ('government', 'en')]),
                   ]

        result = []
        portal = api.portal.get()

        for o in objects:
            tr = [o[0]]
            for td, lang in o[1]:
                if lang == 'root':
                    tr.append(getattr(portal, td, False) and 'Creat' or 'No existeix')
                else:
                    if getattr(portal, lang, False):
                        tr.append(getattr(portal[lang], td, False) and 'Creat' or 'No existeix')
                    else:
                        tr.append('No existeix')
            result.append(tr)
        return result

    def createContent(self):
        """ Method that creates all the default content """
        # TODO Finalize the initial creation code ...
        portal = api.portal.get()
        portal_ca = portal['ca']

        # Create Organ Folder
        root_ca = api.content.create(
            type='genweb.organs.organsfolder',
            title='EETAC',
            container=portal_ca)
        root_ca.description = 'Carpeta Unitat EETAC'
        now = datetime.now()
        past = now - timedelta(days=10)
        future = now + timedelta(days=10)
        # Create Organ
        organ_ca = api.content.create(
            type='genweb.organs.organgovern',
            title='Consell de Govern',
            container=root_ca)
        organ_ca.acronim = 'CDG'
        organ_ca.descripcioOrgan = 'Descripció del Consell de Govern'
        organ_ca.fromMail = 'frommail@organgovern.es'
        organ_ca.adrecaLlista = 'adrecesnotificacio@organgovern.es'
        organ_ca.membresOrgan = '<p>Member 1 composició òrgan</p><p>Member 2 composició òrgan</p><p>Member 3 composició òrgan</p>'
        organ_ca.convidatsPermanentsOrgan = '<p>Member 1 convidat permanent òrgan</p><p>Member 2 convidat permanent òrgan</p><p>Member 3 convidat permanent òrgan</p>'
        organ_ca.adrecaAfectatsLlista = 'adrecaafectats@organ.es'
        organ_ca.bodyMailconvoquing = 'Plantilla missatge de convocatoria de la sessió - Òrgan'
        organ_ca.bodyMailSend = 'Plantilla missatge Enviar missatge - Organ'
        organ_ca.footerMail = '------------------<br/>Signatura del missatge - Òrgan'
        organ_ca.footer = "------------------<br/>Signatura de l'acta - Òrgan"

        # Create session
        session_ca = api.content.create(
            type='genweb.organs.sessio',
            title='Sessió 1/2017 del Consell de Govern',
            container=organ_ca)
        session_ca.llocConvocatoria = 'Barcelona Sala Esdrúixola'
        session_ca.membresConvocats = '-----<p>Persones convocades 1 - Sessió</p><p>Persones convocades 2 - Sessió</p><p>Persones convocades 3 - Sessió</p>'
        session_ca.membresConvidats = '-----<p>Persones convidades 1 - Sessió</p><p>Persones convidades 2 - Sessió</p><p>Persones convidades 3 - Sessió</p>'
        session_ca.llistaExcusats = '<p>Member 1 persones excusades SESSIÓ</p><p>Member 2 persones excusades SESSIÓ</p><p>Member 3 persones excusades SESSIÓ</p>'
        session_ca.noAssistents = '<p>Member 1 persones No assistents SESSIÓ</p><p>Member 2 persones No assistents SESSIÓ</p><p>Member 3 persones No assistents SESSIÓ</p>'
        session_ca.adrecaLlista = 'adrecanotificactio@sessio.es'

        adapter_session = IEventBasic(session_ca)
        adapter_session.start = datetime(2017, 03, 03, 10, 10, 10, 123456, tzinfo=tz)
        adapter_session.end = datetime(2017, 04, 04, 11, 10, 10, 123456, tzinfo=tz)
        data_postprocessing(adapter_session, None)

        # obj = api.content.find(id=session_ca.id, context=organ_ca, depth=1)
        # obj[0].start_time = datetime.datetime(2017, 03, 03, 10, 10, 10, 123456, tzinfo=tz)
        # obj[0].end = datetime.datetime(2017, 04, 04, 11, 10, 10, 123456, tzinfo=tz)
        transaction.commit()
