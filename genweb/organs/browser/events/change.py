# -*- coding: utf-8 -*-
from zExceptions import Redirect
from genweb.organs.utils import addEntryLog
from genweb.organs import _
from genweb.organs import _GW


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
