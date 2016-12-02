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


grok.templatedir("templates")


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


def llistaEstats(context):
    """ Create zope.schema vocabulary from default states. """
    terms = []

    values = context.aq_parent.estatsLlista.splitlines()
    literals = []
    for value in values:
        # color = '#' + value.split('#')[1].rstrip(' ')   # not used here
        literals.append(value.split('#')[0].rstrip(' '))

    for item in literals:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')

        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)
directlyProvides(llistaEstats, IContextSourceBinder)


class ISubpunt(form.Schema):
    """ Tipus Punt: Per a cada Òrgan de Govern es podran crear
        tots els punts que es considerin oportuns
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
    # assigning default proposalPoint number
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


class Edit(dexterity.EditForm):
    """The standard edit form.
    """
    grok.context(ISubpunt)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets['proposalPoint'].mode = HIDDEN_MODE


class View(grok.View):
    """The standard view form.
    """
    grok.context(ISubpunt)
    grok.template('punt_view')

    def isAcord(self):
        if self.context.acordOrgan:
            return True
        return False

    def FilesandDocumentsInside(self):
        """ Retorna files and docs d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                if obj.hiddenfile is True:
                    tipus = 'fa fa-file'
                    document = 'Fitxer intern'
                    labelClass = 'label label-danger'
                else:
                    tipus = 'fa fa-file-o'
                    document = 'Fitxer públic'
                    labelClass = 'label label-success'
            else:
                tipus = 'fa fa-file-text-o'
                document = 'Document'
                labelClass = 'label label-default'

            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile,
                                labelClass=labelClass,
                                content=document))
        return results
