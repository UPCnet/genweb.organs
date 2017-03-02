====================
genweb.organs
====================

Paquet Organs de Govern amb vista jQuery per organitzar Sessions i que s'integra a Genweb.

Instal·lació
============

Primer cal instal·lar i configurar el paquet Genweb UPC i posteriorment s'instal·la aquest paquet.


Information
===========

organs_one_state_workflow -> Tots els elements de tipus genweb.organs són públics i només hi ha un estat.
organs_sessio_workflow --> Workflow aplicat a la Sessió, i conté els estats:
    Planificada / Convocada / Realitzada / Tancada / En correccio (hi ha un fake estat pre_convoque)
