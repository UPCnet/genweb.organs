# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zExceptions import Redirect
import transaction


def sessio_changed(session, event):
    """ If organs.session change WF to convoque, sends email and
        shows the info in the template
    """
    # si passem estat a convocat cal enviar mail de convocatoria...
    if event.transition is None:
        # Quan crees element també executa aquesta acció, i ID no existeix
        # Fem el bypass
        pass
    else:
        if event.transition.id == 'convocar':
            context = aq_inner(session)
            session.reindexObject()
            transaction.commit()
            raise Redirect(context.absolute_url() + '/mailConvocar')
