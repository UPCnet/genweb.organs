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
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from plone.indexer import indexer
from genweb.organs import utils

grok.templatedir("templates")


def llistaEstats(context):
    """ Create vocabulary from Estats Organ. """
    terms = []
    # Al ser subpunt els agafo DOS nivells per sobre
    values = context.aq_parent.aq_parent.estatsLlista
    literals = []
    for value in values.split('<br />'):
        item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '')
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


class ISubpunt(form.Schema):
    """ Tipus Subpunt: Molt similar el PUNT
    """
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

    agreement = schema.TextLine(
        title=_(u'Agreement number'),
        required=False
    )

    acordOrgan = schema.Bool(
        title=_(u'Es un acord?'),
        required=False,
        default=False,
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
    # assign default proposalPoint value to Subpunt
    portal_catalog = getToolByName(data.context, 'portal_catalog')
    folder_path = data.context.absolute_url_path()
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.subpunt'],
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
grok.global_adapter(proposalPoint, name="index_proposalPoint")


class Edit(dexterity.EditForm):
    grok.context(ISubpunt)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets['proposalPoint'].mode = HIDDEN_MODE


class View(grok.View):
    grok.context(ISubpunt)
    grok.template('punt+subpunt_view')

    def isAcord(self):
        if self.context.acordOrgan:
            return True
        return False

    def canViewFiles(self):
        return utils.canViewFiles(self)

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def SubPuntsInside(self):
        return utils.SubPuntsInside(self)
