# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item

from genweb.organs.content.organgovern import IOrgangovern
from genweb.organs.content.sessio import ISessio
from genweb.organs.content.punt import IPunt
from genweb.organs.content.acta import IActa
from genweb.organs.content.organsfolder import IOrgansfolder


class Organgovern(Item):
    implements(IOrgangovern)


class Sessio(Item):
    implements(ISessio)


class Punt(Item):
    implements(IPunt)


class Acta(Item):
    implements(IActa)

class Organsfolder(Item):
    implements(IOrgansfolder)