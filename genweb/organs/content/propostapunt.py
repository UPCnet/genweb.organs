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
from plone.supermodel.directives import fieldset
from AccessControl import Unauthorized
from plone.namedfile.field import NamedBlobFile

grok.templatedir("templates")

class IPropostapunt(form.Schema):
    """ 
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=True
    )

    description = schema.Text(
        title=_(u'label_description', default=u'Summary'),
        required=False,
    )

    directives.widget(text=WysiwygFieldWidget)
    text = schema.Text(
        title=_(u"Text"),
        required=False)

    signsFile = NamedBlobFile(
        title=_(u"Please upload a public file"),
        description=_(u"Published file description"),
        required=False,
    )

    anexFile = NamedBlobFile(
        title=_(u"Please upload a reserved file"),
        description=_(u"Reserved file description"),
        required=False,
    )


class Edit(dexterity.EditForm):
    grok.context(IPropostapunt)


class View(grok.View):
    grok.context(IPropostapunt)
    grok.template('propostapunt_view')

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def canView(self):
        # Permissions to view PUNTS
        # If manager Show all
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

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
