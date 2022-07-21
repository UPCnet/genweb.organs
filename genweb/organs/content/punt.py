# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from collective import dexteritytextindexer
from five import grok
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.directives import dexterity
from plone.directives import form
from plone.indexer import indexer
from plone.supermodel.directives import fieldset

from zope import schema
from zope.interface import directlyProvides
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import unicodedata

grok.templatedir("templates")


def llistaEstats(context):
    """ Create vocabulary from Estats Organ. """
    terms = []
    # Al ser PUNT els agafo 1 nivell per damunt
    values = context.aq_parent.estatsLlista
    literals = []
    for value in values.split('</p>'):
        if value != '':
            item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
            estat = ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8')
            literals.append(estat)

    for item in literals:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)


directlyProvides(llistaEstats, IContextSourceBinder)


class IPunt(form.Schema):
    """ Punt
    """
    fieldset('punt',
             label=_(u'Tab punt'),
             fields=['title', 'proposalPoint', 'defaultContent', 'estatsLlista']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Punt Title'),
        required=True
    )

    form.mode(proposalPoint='hidden')
    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'),
        required=False
    )

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Proposal description"),
        required=False,
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document label"),
        source=llistaEstats,
        required=True,
    )


@form.default_value(field=IPunt['proposalPoint'])
def proposalPointDefaultValue(data):
    # assign default proposalPoint value to Punt
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    path_url = data.context.getPhysicalPath()[1:]
    folder_path = ""
    for path in path_url:
        folder_path += '/' + path
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
        path={'query': folder_path,
              'depth': 1})
    return int(len(values)) + 1


@indexer(IPunt)
def proposalPoint(obj):
    return obj.proposalPoint


grok.global_adapter(proposalPoint, name="index_proposalPoint")


class Edit(dexterity.EditForm):
    grok.context(IPunt)


class View(grok.View, UtilsFirmaDocumental):
    grok.context(IPunt)
    grok.template('punt+subpunt_view')

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def getColor(self):
        # assign custom colors on organ states
        estat = self.context.estatsLlista
        # Only 1 level
        values = self.context.aq_parent.aq_parent.estatsLlista
        color = '#777777'
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def SubPuntsInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        if values:
            for obj in values:
                item = obj.getObject()
                if item.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"sense numeracio")
                else:
                    agreement = ''
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    item_path=item.absolute_url_path(),
                                    state=item.estatsLlista,
                                    agreement=agreement,
                                    css=utils.getColor(obj)))
        return results

    def canView(self):
        # Permissions to view PUNTS
        # If manager Show all
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada':
                return True
            elif estatSessio == 'realitzada':
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized
