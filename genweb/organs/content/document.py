# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone import api
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.supermodel.directives import fieldset
from AccessControl import Unauthorized
from genweb.organs import utils

grok.templatedir("templates")


class IDocument(form.Schema):
    """ Document: Per marcar si són públics o privats """

    fieldset('document',
             label=_(u'Tab document'),
             fields=['title', 'description', 'defaultContent', 'alternateContent']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    dexteritytextindexer.searchable('title')
    description = schema.Text(
        title=_PMF(u'label_description', default=u'Summary'),
        description=_PMF(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Contingut public"),
        description=_(u"Default content shown in the document view"),
        required=False,
    )

    directives.widget(alternateContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('alternateContent')
    alternateContent = schema.Text(
        title=_(u"Alternate description"),
        description=_(u"Content used to hide protected content"),
        required=False,
    )


@form.default_value(field=IDocument['title'])
def titleDefaultValue(data):
    # fica el títol de document
    return data.context.Title()


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IDocument)


class View(grok.View):
    grok.context(IDocument)
    grok.template('document_view')

    def viewDocumentPublic(self):
        """ Cuando se muestra la parte pública del documento
        """
        if utils.isManager(self):
            return True
        organ_tipus = self.context.aq_parent.organType  # 1 level up
        if self.context.defaultContent and self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if utils.isMembre(self):
                    return False
                else:
                    return True
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isAfectat(self)):
                    return True
                else:
                    return False
        elif self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
        elif self.context.defaultContent:
            if organ_tipus == 'open_organ':
                return True
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
        else:
            raise Unauthorized

    def viewDocumentReserved(self):
        """ Cuando se muestra la parte privada del documento
        """
        if utils.isManager(self):
            return True
        organ_tipus = self.context.aq_parent.organType  # 1 level up
        if self.context.defaultContent and self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    raise False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    raise False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    raise False
        elif self.context.alternateContent:
            if organ_tipus == 'open_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    raise False
            elif organ_tipus == 'restricted_to_members_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
            elif organ_tipus == 'restricted_to_affected_organ':
                if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                    return True
                else:
                    return False
        elif self.context.defaultContent:
            if organ_tipus == 'open_organ':
                    return True
        else:
            raise Unauthorized

    def canView(self):
        # Permissions to view DOCUMENT
        # If manager Show all
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.aq_parent.organType  # 1 level up
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
