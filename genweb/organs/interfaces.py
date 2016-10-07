# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from genweb.theme.browser.interfaces import IGenwebTheme
from plone.theme.interfaces import IDefaultPloneLayer


class IGenwebOrgansLayer(IGenwebTheme): 
    """Marker interface that defines a Zope 3 browser layer."""
