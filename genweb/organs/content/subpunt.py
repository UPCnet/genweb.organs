# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from collective import dexteritytextindexer
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from z3c.form import form
from plone.indexer import indexer
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import unicodedata


def llistaEstats(context):
    """ Create vocabulary from Estats Organ """
    terms = []
    # Al ser SUBPUNT els agafo 2 nivells per damunt
    values = context.aq_parent.aq_parent.estatsLlista
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


class ISubpunt(model.Schema):
    """ Subpunt: Molt similar el PUNT
    """
    fieldset('subpunt',
             label=_(u'Tab subpunt'),
             fields=['title', 'proposalPoint', 'defaultContent', 'estatsLlista']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Subpunt Title'),
        required=True
    )

    directives.mode(proposalPoint='hidden')
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
        title=_(u"Agreement and document labels"),
        source=llistaEstats,
        required=True,
    )


@form.default_value(field=ISubpunt['proposalPoint'])
def proposalPointDefaultValue(data):
    # Assign default proposalPoint value to Subpunt
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    path_url = data.context.getPhysicalPath()[1:]
    folder_path = ""
    for path in path_url:
        folder_path += '/' + path

    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
        path={'query': folder_path,
              'depth': 1})
    subpunt_id = int(len(values)) + 1
    if data.context.proposalPoint is None:
        data.context.proposalPoint = 1
        punt_id = 1
    else:
        punt_id = data.context.proposalPoint
    return str(punt_id) + '.' + str(subpunt_id)


@indexer(ISubpunt)
def proposalPoint(obj):
    return obj.proposalPoint


class Edit(form.EditForm):
    pass


class View(BrowserView, UtilsFirmaDocumental):
    index = ViewPageTemplateFile("templates/punt+subpunt_view.pt")
    def __call__(self):
        return self.index()

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def SubPuntsInside(self):
        return None

    def getColor(self):
        estat = self.context.estatsLlista
        values = self.context.aq_parent.aq_parent.aq_parent.estatsLlista
        color = '#777777'
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def canView(self):
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
