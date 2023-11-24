# -*- coding: utf-8 -*-
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget

import z3c.form.browser.text
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


class ISelectUsersActaInputWidget(z3c.form.interfaces.ITextWidget):
    pass


class SelectUsersActaInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):
    zope.interface.implementsOnly(ISelectUsersActaInputWidget)

    klass = u'select-users-acta-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SelectUsersActaInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, SelectUsersActaInputWidget(request))


class ISelectUsersOtherInputWidget(z3c.form.interfaces.ITextWidget):
    pass

class SelectUsersOtherInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):
    zope.interface.implementsOnly(ISelectUsersOtherInputWidget)

    klass = u'select-users-other-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SelectUsersOtherInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, SelectUsersOtherInputWidget(request))