# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from zExceptions import Redirect
from zope.globalrequest import getRequest

from genweb.organs import _
from genweb.organs import _GW
from genweb.organs.firma_documental.utils import estatFirmaActa
from genweb.organs.firma_documental.utils import hasFirmaActa
from genweb.organs.utils import addEntryLog
from genweb.organs.utils import get_organ

import transaction


def sessio_changed(session, event):
    """ If organs.session change WF to convoque, sends email and
        shows the info in the template
    """
    # si passem estat a convocat cal enviar mail de convocatoria...
    try:
        # old = _GW(event.status['review_state'])
        new = _GW(event.transition.new_state_id)
        # message = (old) + ' →2 ' + (new)
        addEntryLog(session, None, _(u'Changed workflow state'), new)  # add log
    except:
        addEntryLog(session, None, _(u'New session created'), session.Title())  # add log

    if event.transition is None:
        # Quan crees element també executa aquesta acció, i ID no existeix
        # Fem el bypass
        pass
    else:
        """ Previ a l'enviament del missatge et troves en un estat intermig,
            creat només per això, que es diu Convocant (no es veu enlloc)
        """
        if event.transition.id == 'convocant':
            raise Redirect(session.absolute_url() + '/mail_convocar')

        if event.transition.id == 'tancar':
            organ = get_organ(session)
            if organ.visiblegdoc:
                estat_firma = estatFirma(session)
                if not estat_firma or ['class'] != 'signada':
                    IStatusMessage(getRequest()).addStatusMessage(
                        _(u'No es pot tancar la sessió si no està signada l\'acta.'), 'alert')
                    raise Redirect(session.absolute_url())
            member = api.user.get(username='admin')
            user = member.getUser()
            session.changeOwnership(user, recursive=False)
            owners = session.users_with_local_role("Owner")
            session.manage_delLocalRoles(owners)
            if user.getId() == 'admin':
                session.manage_setLocalRoles(user.getId(), ["Owner"])
            else:
                session.manage_setLocalRoles(user._id, ["Owner"])
            session.reindexObjectSecurity()
            transaction.commit()


def estatFirma(context):
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(context.getPhysicalPath())
    actes = portal_catalog.searchResults(
        portal_type=['genweb.organs.acta'],
        sort_on='created',
        sort_order='reverse',
        path={'query': folder_path, 'depth': 1}
    )
    for acta in actes:
        acta_obj = acta.getObject()
        if hasFirmaActa(acta_obj):
            return estatFirmaActa(acta_obj)

    return None