# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item

from genweb.organs.content.organgovern import IOrgangovern


class Organgovern(Item):
    implements(IOrgangovern)
