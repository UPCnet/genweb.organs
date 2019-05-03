# -*- coding: utf-8 -*-

from zope import schema
from z3c.form import button
from plone.supermodel import model
from plone.app.registry.browser import controlpanel
from Products.statusmessages.interfaces import IStatusMessage

from genweb.organs import _


class IOrgansSettings(model.Schema):
    model.fieldset(
        'Indicadors',
        _(u'Indicadors'),
        fields=['service_id', 'ws_endpoint', 'ws_key'],
    )

    service_id = schema.TextLine(
        title=_(u"Identificador al servei web d'Indicadors"),
        description=_(u"Identificador d'Òrgans de govern al servei web"),
        required=False,
    )

    ws_endpoint = schema.TextLine(
        title=_(u"URL del servei web"),
        required=False,
    )

    ws_key = schema.Password(
        title=_(u"API key del servei web"),
        required=False,
    )


class OrgansSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IOrgansSettings
    label = _(u'Paràmetres de configuració de Genweb Organs')

    def updateFields(self):
        super(OrgansSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(OrgansSettingsEditForm, self).updateWidgets()

    def fix_password_fields(self, data):
        """
        Keep the stored value for the password fields not updated in the
        current request, i.e. those containing a None value.
        This method is needed since the password fields are not filled with
        their stored value when the edit form is loaded.
        """
        if not data['ws_key']:
            data['ws_key'] = self.getContent().ws_key

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.fix_password_fields(data)
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u'Changes saved'), 'info')
        self.context.REQUEST.RESPONSE.redirect('@@organs-settings')

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u'Edit cancelled'), 'info')
        self.request.response.redirect(
            '%s/%s' % (self.context.absolute_url(), self.control_panel_view))


class OrgansSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = OrgansSettingsEditForm
