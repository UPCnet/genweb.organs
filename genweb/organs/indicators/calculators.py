from Products.CMFCore.utils import getToolByName
from plone import api
from genweb.core.indicators import Calculator
from genweb.organs.indicators.data_access import (
    list_organs_by_review_state,
    list_sessions_by_delta_and_review_state,
    list_acords_by_estat_aprovacio_and_delta_and_review_state)


class OrganNumber(Calculator):
    def calculate(self):
        catalog = api.portal.get_tool('portal_catalog')
        return len(
            list_organs_by_review_state(catalog))


class SessioNumberEstatConvocat(Calculator):
    def calculate(self):
        catalog = api.portal.get_tool('portal_catalog')
        return len(
            list_sessions_by_delta_and_review_state(
                catalog, None, ('convocada',)))


class SessioNumberDeltaMonth(Calculator):
    def calculate(self):
        catalog = api.portal.get_tool('portal_catalog')
        return len(list_sessions_by_delta_and_review_state(
            catalog, -30))


class AcordNumberEstatAprovat(Calculator):
    def calculate(self):
        catalog = api.portal.get_tool('portal_catalog')
        return len(
            list_acords_by_estat_aprovacio_and_delta_and_review_state(
                catalog, 'Aprovat', None, ('intranet', 'published')))


class AcordNumberEstatAprovatDeltaMonth(Calculator):
    def calculate(self):
        catalog = api.portal.get_tool('portal_catalog')
        return len(
            list_acords_by_estat_aprovacio_and_delta_and_review_state(
                catalog, 'Aprovat', -30, ('intranet', 'published')))
