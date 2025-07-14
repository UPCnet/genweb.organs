# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from Products.Five.browser import BrowserView

from genweb.organs import _
from genweb.organs.content.sessio.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs.utils import addEntryLog
from genweb.organs import utils

import transaction
import unicodedata


class ManualImport(BrowserView):
    """ Browser view for manual structure creation
    """

    def __call__(self):
        """ Process the form submission """
        # Check permissions
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property and self.context.migrated is True:
            raise Unauthorized

        try:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if not utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                raise Unauthorized
        except:
            raise Unauthorized

        # Get form data
        message = self.request.form.get('form.widgets.message', '')
        action = self.request.form.get('form.buttons.send', '')

        if action == 'Cancel·la' or not action:
            message = _(u"Operation Cancelled.")
            IStatusMessage(self.request).addStatusMessage(message, type="warning")
            return self.request.response.redirect(self.context.absolute_url())

        if not message or message.strip() == '':
            message = 'Falten els valors dels punts. Cap canvi realitzat.'
            lang = self.context.language
            if lang == 'es':
                message = "Faltan los valores de los puntos. No se ha realizado ningún cambio."
            if lang == 'en':
                message = "Required values missing. No changes made."
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return self.request.response.redirect(self.context.absolute_url())

        """ Adding message information to context in annotation format """
        addEntryLog(self.context, None, _(u'Massive agreements imported'), '')

        # Creating new objects
        text = message

        # Obtener el órgano usando utils.get_organ como en createElement
        organ = utils.get_organ(self.context)
        print(f"DEBUG: organ encontrado = {organ}")

        values = organ.estatsLlista
        if hasattr(values, 'raw'):
            values = values.raw
        value = values.split('</p>')[0]
        item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
        defaultEstat = ' '.join(item_net.split()[:-1]).lstrip()

        # --- Numeración de acuerdos ---
        acronim = getattr(organ, 'acronim', '') or ''
        any = str(self.context.start.year) if hasattr(self.context, 'start') else str(api.portal.get_localized_time())[:4]
        numsessio = getattr(self.context, 'numSessio', '01')
        idacord = 1
        # ---

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        puntsInFolder = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        index = len(puntsInFolder) + 1

        content = text.splitlines()
        subindex = 0
        previousPuntContainer = None
        errors = None
        for line in content:
            if len(line) == 0:
                continue
            else:
                if line.startswith((' ', '\t')) is False:
                    # No hi ha blanks, es un punt o un acord
                    # Obtenim una A o un P per saber si es Acord o Punt
                    portal_type = line.lstrip().rstrip().split(' ')[0].upper()
                    if str(portal_type) == 'A':  # Es tracta d'un acord
                        line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.acord',
                                title=line,
                                container=self.context)
                        # Numerar acuerdo
                        printid = '{0}'.format(str(idacord).zfill(2))
                        obj.agreement = f"{acronim}/{any}/{numsessio}/{printid}"
                        obj.omitAgreement = False
                        idacord += 1
                    elif str(portal_type) == 'P':  # Es tracta d'un punt
                        line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.punt',
                                title=line,
                                container=self.context)
                    else:  # Supossem que per defecte sense espais es un Punt
                        line = line.lstrip().rstrip()
                        with api.env.adopt_roles(['OG1-Secretari']):
                            obj = api.content.create(
                                type='genweb.organs.punt',
                                title=line,
                                container=self.context)
                    obj.proposalPoint = str(index)
                    obj.estatsLlista = defaultEstat
                    index = index + 1
                    subindex = 1
                    previousPuntContainer = obj
                    obj.reindexObject()
                else:
                    # hi ha blanks, es un subpunt o un acord
                    portal_type = line.lstrip().rstrip().split(' ')[0].upper()
                    if previousPuntContainer.portal_type == 'genweb.organs.punt':
                        if str(portal_type) == 'A':  # Es tracta d'un acord
                            line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.acord',
                                    title=line,
                                    container=previousPuntContainer)
                            # Numerar acuerdo
                            printid = '{0}'.format(str(idacord).zfill(2))
                            newobj.agreement = f"{acronim}/{any}/{numsessio}/{printid}"
                            newobj.omitAgreement = False
                            idacord += 1
                        elif str(portal_type) == 'P':  # Es tracta d'un punt
                            line = ' '.join(line.lstrip().rstrip().split(' ')[1:])
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.subpunt',
                                    title=line,
                                    container=previousPuntContainer)
                        else:  # Supossem que per defecte sense espais es un Punt
                            line = line.lstrip().rstrip()
                            with api.env.adopt_roles(['OG1-Secretari']):
                                newobj = api.content.create(
                                    type='genweb.organs.subpunt',
                                    title=line,
                                    container=previousPuntContainer)

                        newobj.proposalPoint = str(index - 1) + '.' + str(subindex)
                        newobj.estatsLlista = defaultEstat
                        newobj.reindexObject()
                        subindex = subindex + 1
                    else:
                        # dintre d'un acord no podem crear res...
                        errors = _(u"No s'han creat tot els elements perque no segueixen la norma. Dintre d'un Acord no es pot afeigr res.")
                        subindex = subindex - 1

        transaction.commit()

        if errors:
            IStatusMessage(self.request).addStatusMessage(errors, type="error")
            return self.request.response.redirect(self.context.absolute_url())
        else:
            message = "S'han creats els punts indicats."
            lang = self.context.language
            if lang == 'es':
                message = "Se han creado los puntos indicados."
            if lang == 'en':
                message = "Indicated fields have been created."
            IStatusMessage(self.request).addStatusMessage(message, type="success")
            return self.request.response.redirect(self.context.absolute_url())
