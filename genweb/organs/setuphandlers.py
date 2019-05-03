# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName


fields_to_index = [('estatAprovacio', 'FieldIndex'),
                   ('dataSessio', 'DateIndex')]


def add_catalog_indexes(catalog):
    indexables = []
    indexes = catalog.indexes()
    for name, meta_type in fields_to_index:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
    if indexables:
        catalog.manage_reindexIndex(ids=indexables)


def setupVarious(context):
    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    add_catalog_indexes(catalog)
