# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item

from genweb.organs.content.organgovern import IOrgangovern
from genweb.organs.content.sessio import ISessio


class Organgovern(Item):
    implements(IOrgangovern)


class Sessio(Item):
    implements(ISessio)
