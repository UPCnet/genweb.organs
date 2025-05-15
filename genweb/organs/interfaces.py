"""Module where all interfaces, events and exceptions live."""
from genweb6.theme.interfaces import IGenweb6ThemeLayer


class IGenwebOrgansLayer(IGenweb6ThemeLayer):
    """Marker interface that defines a Zope 3 browser layer."""
