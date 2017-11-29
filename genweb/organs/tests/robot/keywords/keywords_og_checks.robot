*** Settings ***

Library  Selenium2Library

Resource  keywords_og.robot


*** Keywords ***

Log Check If
  [Arguments]  ${CONDITION}  ${STATUS}  ${CHECK_MSG}
  ${CHECK_MSG} =  Run Keyword If  ${CONDITION}  Set Variable  ${CHECK_MSG}
  ...  ELSE  Set Variable  NO ${CHECK_MSG}
  ${MSG_OK} =  Set Variable  \t* ${CHECK_MSG} OK
  ${MSG_ERROR} =  Set Variable  \t* ${CHECK_MSG} Error
  Run Keyword If  ${CONDITION} == ${STATUS}  Log  ${MSG_OK}  console=True
  ...  ELSE  Log  ${MSG_ERROR}  console=True

Check if can view portlet Navigation
  [Arguments]  ${CONDITION}=True
  Go To  ${PLONE_URL}/ca
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="portlet-navigation-tree"]/li/div/a/span[text()="${FOLDER_NAME}"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el portlet de navegació:

Check if can view list organs
  [Arguments]  ${CONDITION}=True
  Go To  ${FOLDER_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[text()="${OG_NAME}"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el llistat d'organs:

Check if can view list organs and types
  [Arguments]  ${TYPE}  ${CONDITION}=True
  Go To  ${FOLDER_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[text()="${OG_NAME}"]/../../td/span[text()="${TYPE}"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el llistat d'organs amb els tipus:

Check if can view OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="documentFirstHeading" and text()="${OG_NAME}"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure l'OG:

Check if can view tab Sessions in a OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Sessions"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Sessions> dintre de l'OG:

Check if can view tab Composition in a OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Composició"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Composició> dintre de l'OG:

Check if can view tab Agreements in a OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Acords"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Acords> dintre de l'OG:

Check if can view tab Acts in a OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Actes"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Actes> dintre de l'OG:

Check if can view session in a OG
  [Arguments]  ${CONDITION}=True
  Go To  ${OG_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="sessionsTab"]/table/tbody/tr/td/a[text()="${SESSION_NAME}"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la sessió dintre de l'OG:

Check if can view tab Call in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Convocatòria"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Convocatòria> dintre de la sessió:

Check if can view tab Members in a session
  [Arguments]   ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Membres"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Membres> dintre de la sessió:

Check if can view tab Agreements in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Acords"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Acords> dintre de la sessió:

Check if can view tab Act in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Acta"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Acta> dintre de la sessió:

Check if can view tab History in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //ul[@id="tabs"]/li/a[text()="Historial"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la tab <Historial> dintre de la sessió:

Check if can view button Add informational point in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[@class="btn btn-info"]/span[text()="Afegeix punt informatiu"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Afegeix punt informatiu> dintre de la sessió:

Check if can view button Add agreement in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[@class="btn btn-info"]/span[text()="Afegeix acord"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Afegeix acord> dintre de la sessió:

Check if can view button Agile creation in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[@class="btn btn-info"]/span[text()="Creació àgil"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Creació àgil> dintre de la sessió:

Check if can view button Number points in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[@class="btn btn-info"]/span[text()="Numera punts"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Numera punts> dintre de la sessió:

Check if can view button Number agreements in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[@class="btn btn-info"]/span[text()="Numera acords"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Numera acords> dintre de la sessió:

Check if can add Point in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-subpunt"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Punts informatius> dintre d'un punt informatiu:

Check if can add Agreement in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-acord"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Acords> dintre d'un punt informatiu:

Check if can add Files in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-file"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Fitxers> dintre d'un punt informatiu:

Check if can add Documents in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-document"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Documents> dintre d'un punt informatiu:

Check if can view public file in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //li[contains(a,"${PUBLIC_FILE_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure <Fitxers publics> dintre d'un punt informatiu:

Check if can view restricted file in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //li[contains(a,"${RESTRICTED_FILE_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure <Fitxers restringits> dintre d'un punt informatiu:

Check if can view public document in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //li[contains(a,"${PUBLIC_DOCUMENT_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure <Documents publics> dintre d'un punt informatiu:

Check if can view restricted document in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //li[contains(a,"${RESTRICTED_DOCUMENT_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure <Documents restringits> dintre d'un punt informatiu:

Check if can add Points from the top menu
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-punt"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Punts informatius> desde el menú superior:

Check if can add Act from the top menu
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-acta"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Actes> desde el menú superior:

Check if can add Agreement from the top menu
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="genweb-organs-acord"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot afegir <Acords> desde el menú superior:

Check if can view the edit bar in a point
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="contentview-edit"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot editar <Punts informatius>:

Check if can view the edit bar in a agreement
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}/${AGREEMENT_NAME}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="contentview-edit"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot editar <Acords>:

Check if can view the edit bar in a act
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}/${ACT_NAME}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="contentview-edit"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot editar <Actes>:

Check if can view the edit bar in a subpoint
  [Arguments]  ${CONDITION}=True
  Go To  ${POINT_URL}/${SUBPOINT_NAME}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="contentview-edit"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot editar <Subpunts informatius>:

Check if can view public documents in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_DOCUMENT_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un document públic en la llista de la sessió:

Check if the public document is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_DOCUMENT} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_DOCUMENT_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_DOCUMENT}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_DOCUMENT_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El document públic de la llista s'obre en la mateixa finesta:

Check if can view restricted documents in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_DOCUMENT_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un document restringit en la llista de la sessió:

Check if the restricted document is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_DOCUMENT} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_DOCUMENT_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_DOCUMENT}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_DOCUMENT_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El document restringit de la llista s'obre en la mateixa finesta:

Check if can view public-restricted documents in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${DOCUMENT_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un document amb part pública i restringida en la llista de la sessió:

Check if the public-restricted document is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_DOCUMENT} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${DOCUMENT_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_DOCUMENT}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${DOCUMENT_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El document amb part pública i restringida de la llista s'obre en la mateixa finesta:

Check if can view the public part in a document
  [Arguments]  ${CONDITION}=True
  Go To  ${DOCUMENT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="content-core"]/span[contains(h3, "Contingut públic") and contains(p, "${PUBLIC_CONTENT}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la part pública en un document:

Check if can view the private part in a document
  [Arguments]  ${CONDITION}=True
  Go To  ${DOCUMENT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@id="content-core"]/span[contains(h3, "Contingut restringit") and contains(p, "${RESTRICTED_CONTENT}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la part restingida en un document:

Check if can view public files in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_FILE_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un fitxer públic en la llista de la sessió:

Check if the public file is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_FILE} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_FILE_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_FILE}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${PUBLIC_FILE_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El fitxer públic de la llista s'obre en la mateixa finesta:

Check if can view restricted files in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_FILE_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un fitxer restringit en la llista de la sessió:

Check if the restricted file is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_FILE} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_FILE_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_FILE}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${RESTRICTED_FILE_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El fitxer restringit de la llista s'obre en la mateixa finesta:

Check if can view public-restricted files in the drop-down of session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${FILE_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure un fitxer amb part pública i restringida en la llista de la sessió:

Check if the public-restricted file is opened in the same window
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${EXIST_FILE} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@class="filesinTable"]/a[contains(., "${FILE_NAME}")]
  ${STATUS} =  Run Keyword If  ${EXIST_FILE}
  ...  Run Keyword And Return Status  Page Should Not Contain Element  //*[@class="filesinTable"]/a[contains(., "${FILE_NAME}") and @target="_blank"]
  ...  ELSE  Set Variable  False
  Log Check If  ${CONDITION}  ${STATUS}  El fitxer amb part pública i restringida de la llista s'obre en la mateixa finesta:

Check if can view the public part in a file
  [Arguments]  ${CONDITION}=True
  Go To  ${FILE_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //div[contains(h3, "Fitxer públic")]/p[contains(a, "${PDF_PUBLIC_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la part pública en un fitxer:

Check if can view the private part in a file
  [Arguments]  ${CONDITION}=True
  Go To  ${FILE_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //div[contains(h3, "Fitxer restringit")]/p[contains(a, "${PDF_RESTRICTED_NAME}")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure la part restingida en un fitxer:

Check if can view button Member message in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@alt="Missatge als membres"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Missatge als membres> dintre de la sessió:

Check if can view button Presentation mode in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@alt="Mode presentació"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Mode presentació> dintre de la sessió:

Check if can view button Send summary in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@alt="Envia resum de la sessió"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Envia resum> dintre de la sessió:

Check if can view button Print in a session
  [Arguments]  ${CONDITION}=True
  Go To  ${SESSION_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //*[@alt="Imprimeix ordre del dia"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Imprimeix> dintre de la sessió:

Check if can view button Preview in a act
  [Arguments]  ${CONDITION}=True
  Go To  ${ACT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //button[@data-target="#previewModal"]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Vista prèvia> dintre d'un acta:

Check if can view button Download PDF file in a act
  [Arguments]  ${CONDITION}=True
  Go To  ${ACT_URL}
  ${STATUS} =  Run Keyword And Return Status  Wait Until Page Contains Element  //a[contains(span, "Descarrega acta en PDF")]
  Log Check If  ${CONDITION}  ${STATUS}  Pot veure el botó <Descarrega acta en PDF> dintre d'un acta:
