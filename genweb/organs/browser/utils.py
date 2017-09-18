# -*- coding: utf-8 -*-
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from genweb.organs.interfaces import IGenwebOrgansLayer


class changeInitialProposalPoint(grok.View):
    # After migration, there was an error...
    # Point 0 must be Informat, instead of Aprovat
    grok.context(IDexterityContent)
    grok.name('change_proposal_after_migration')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        items = api.content.find(path='/', portal_type='genweb.organs.punt')
        results = []
        for item in items:
            value = item.getObject()
            if value.proposalPoint is '0':
                value.estatsLlista = 'Informat'
                results.append(dict(title=item.Title,
                                    path=item.getURL(),
                                    proposalPoint=value.proposalPoint,
                                    estat=value.estatsLlista))
        return results
