# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
import unicodedata
from plone.indexer import indexer
from genweb.organs import utils
from AccessControl import Unauthorized
from plone.supermodel.directives import fieldset

grok.templatedir("templates")


def llistaEstats(context):
    """ Create vocabulary from Estats Organ. """
    terms = []
    # Els ACORDS NOMES van dintre de sessio o de punt
    # Al ser acord he de mirar si està dintre d'una sessio o d'un punt

    # En mode add or en mode edit, mirar 1nivell(SESSIO) o 2nivells(PUNT)
    if context.aq_parent.portal_type == 'genweb.organs.sessio' or context.portal_type == 'genweb.organs.sessio':
        values = context.aq_parent.estatsLlista
    if context.aq_parent.portal_type == 'genweb.organs.punt' or context.portal_type == 'genweb.organs.punt':
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


class IAcord(form.Schema):
    """ Acord """

    fieldset('acord',
             label=_(u'Tab acord'),
             fields=['title', 'proposalPoint', 'agreement', 'defaultContent', 'estatsLlista']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Acord Title'),
        required=True
    )
    form.mode(proposalPoint='hidden')
    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'),
        required=False,
    )

    form.mode(agreement='hidden')
    agreement = schema.TextLine(
        title=_(u'Agreement number'),
        required=False,
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


@form.default_value(field=IAcord['proposalPoint'])
def proposalPointDefaultValue(data):
    # assign default proposalPoint value to Punt
    portal_catalog = getToolByName(data.context, 'portal_catalog')
    path_url = data.context.getPhysicalPath()[1:]
    folder_path = ""
    for path in path_url:
        folder_path += '/' + path

    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord', 'genweb.organs.subpunt'],
        path={'query': folder_path,
              'depth': 1})
    subpunt_id = int(len(values)) + 1
    if data.context.portal_type == 'genweb.organs.sessio':
        return subpunt_id
    else:
        if data.context.proposalPoint is None:
            data.context.proposalPoint = 1
            punt_id = 1
        else:
            punt_id = data.context.proposalPoint
        return str(punt_id) + '.' + str(subpunt_id)


@indexer(IAcord)
def proposalPoint(obj):
    return obj.proposalPoint


grok.global_adapter(proposalPoint, name="index_proposalPoint")


class Edit(dexterity.EditForm):
    grok.context(IAcord)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class View(grok.View):
    grok.context(IAcord)
    grok.template('acord_view')

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def getColor(self):
        # assign custom colors on organ states
        estat = self.context.estatsLlista
        values = self.context.aq_parent.aq_parent.estatsLlista
        color = '#777777'
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def AcordTitle(self):
        if self.context.agreement:
            return _(u'[Acord ') + self.context.agreement + ']'
        else:
            return _(u'[Acord sense numeracio]')

    def canView(self):
        # Permissions to view ACORDS. Poden estar a 1 i 2 nivells
        # If manager Show all
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)

        organ_tipus = self.context.organType  # TODO: WHY??? Funciona amb 1 i 2 level up

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            else:
                raise Unauthorized
