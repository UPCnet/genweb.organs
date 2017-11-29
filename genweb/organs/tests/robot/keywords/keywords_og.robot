*** Settings ***

Library  Selenium2Library

Resource  keywords.robot


*** Variables ***

### NAMES ###

${FOLDER_NAME}  carpeta
${OG_NAME}  organ
${SESSION_NAME}  sessio
${AGREEMENT_NAME}  acord
${ACT_NAME}  acta
${POINT_NAME}  punt-informatiu
${SUBPOINT_NAME}  subpunt-informatiu
${FILE_NAME}  fitxer-complet
${PUBLIC_FILE_NAME}  fitxer-public
${RESTRICTED_FILE_NAME}  fitxer-restringit
${DOCUMENT_NAME}  document-complet
${PUBLIC_DOCUMENT_NAME}  document-public
${RESTRICTED_DOCUMENT_NAME}  document-restringit

${PDF_PUBLIC_NAME}  pdf_public.pdf
${PDF_RESTRICTED_NAME}  pdf_restringit.pdf
${PUBLIC_CONTENT}  public
${RESTRICTED_CONTENT}  restringit

### USERS ###

${VALIDATED_USER_NAME}  validat
${MEMBER_USER_NAME}  membre
${AFFECTED_USER_NAME}  afectat
${EDITOR_USER_NAME}  editor
${SECRETARY_USER_NAME}  secretari

### URLS ###

${FOLDER_URL}  ${PLONE_URL}/ca/${FOLDER_NAME}
${OG_URL}  ${FOLDER_URL}/${OG_NAME}
${SESSION_URL}  ${OG_URL}/${SESSION_NAME}
${ACT_URL}  ${SESSION_URL}/${ACT_NAME}
${POINT_URL}  ${SESSION_URL}/${POINT_NAME}
${DOCUMENT_URL}  ${POINT_URL}/${DOCUMENT_NAME}
${FILE_URL}  ${POINT_URL}/${FILE_NAME}

### PATHS ###

${PUBLIC_FILE_PATH}  ${CURDIR}/pdf/${PDF_PUBLIC_NAME}
${RESTRICTED_FILE_PATH}  ${CURDIR}/pdf/${PDF_RESTRICTED_NAME}


*** Keywords ***

Initial configurations
  Set Selenium Timeout  2s
  Login as admin
  the default directories have been created
  OrgansFolder added in a LRF
  Go to  ${PLONE_URL}

OrgansFolder added in a LRF
  Go to  ${PLONE_URL}/portal_types/LRF/manage_propertiesForm
  Select From List By Label  name=allowed_content_types:list:string  genweb.organs.organsfolder
  Click Button  name=manage_editProperties:method
  Log  Afegit els tipus de contingut OrgansFolder en LRF  console=True

Create user OG
  [Arguments]  ${USER_NAME}  ${TYPE}=None
  Login as admin
  Go To  ${PLONE_URL}/@@usergroup-userprefs
  Confirm action
  Set Selenium Speed  0.2
  Click Element  form.button.AddUser
  Wait Until Page Contains Element  form.username
  Input Text  form.username  ${USER_NAME}
  Input Text  form.email  ${USER_NAME}@mailinator.com
  Input Password  form.password  ${USER_NAME}
  Input Password  form.password_ctl  ${USER_NAME}
  Click Element  form.actions.register
  ${STATUS} =  Run Keyword And Return Status  Should Be Equal	 ${TYPE}  None
  Run Keyword Unless  ${STATUS}  Add type to user  ${USER_NAME}  ${TYPE}
  Set Selenium Speed  0

Add type to user
  [Arguments]  ${USER_NAME}  ${TYPE}
  Set Selenium Speed  0.2
  Wait Until Page Contains Element  xpath=//a[@title="${USER_NAME}"]
  Select Checkbox  xpath=//a[@title="${USER_NAME}"]/../../td/input[@value="${TYPE}"]
  Click Element  form.button.Modify
  Set Selenium Speed  0

Add portlet Navigation
  Go To  ${PLONE_URL}/ca/benvingut/@@manage-homeportlets
  Confirm action
  Click Element  //*[@id="portletselectorform"]/div/button
  Click Element  //*[@id="portletselectorform"]/div/ul/li/a[text()="Menú de navegació"]
  Input Text  name=form.topLevel  0
  Input Text  name=form.bottomLevel  2
  Save form
  Log  Creat portlet de navegació  console=true

Create a organs folder
  Go To  ${PLONE_URL}/ca/++add++genweb.organs.organsfolder
  Input Text  name=form.widgets.IBasic.title  ${FOLDER_NAME}
  Save form
  Log  Creat la carpeta d'organs  console=true

Create a OG
  [Arguments]  ${TYPE}
  Go To  ${FOLDER_URL}/++add++genweb.organs.organgovern
  Input Text  name=form.widgets.title  ${OG_NAME}
  Input Text  name=form.widgets.fromMail  ${MEMBER_USER_NAME}@mailinator.com
  Select From List By Value  name=form.widgets.organType:list  ${TYPE}
  Save form
  Input F_Textarea  form-widgets-membresOrgan_ifr  ${MEMBER_USER_NAME}
  Input F_Textarea  form-widgets-convidatsPermanentsOrgan_ifr  ${MEMBER_USER_NAME}
  Input Textarea  form.widgets.adrecaLlista  ${MEMBER_USER_NAME}@mailinator.com
  Save form

Create a session
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.sessio
  Input Text  name=form.widgets.title  ${SESSION_NAME}
  Select Checkbox  name=form.widgets.IEventBasic.whole_day:list
  Select Checkbox  name=form.widgets.IEventBasic.open_end:list
  Save form
  Log  \tCreat la sessió  console=True

Create a agreement
  [Arguments]  ${URL}
  Create a simple element  ${URL}/++add++genweb.organs.acord  ${AGREEMENT_NAME}
  Log  \t\tCreat l'acord  console=True

Create a act
  [Arguments]  ${URL}
  Create a simple element  ${URL}/++add++genweb.organs.acta  ${ACT_NAME}
  Log  \t\tCreat l'acte  console=True

Create a point
  [Arguments]  ${URL}
  Create a simple element  ${URL}/++add++genweb.organs.punt  ${POINT_NAME}
  Log  \t\tCreat el punt d'informació  console=True

Create a subpoint
  [Arguments]  ${URL}
  Create a simple element  ${URL}/++add++genweb.organs.subpunt  ${SUBPOINT_NAME}
  Log  \t\t\tCreat el subpunt d'informació  console=True

Create a document
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.document
  Input Text  name=form.widgets.title  ${DOCUMENT_NAME}
  Input F_Textarea  form-widgets-defaultContent_ifr  ${PUBLIC_CONTENT}
  Input F_Textarea  form-widgets-alternateContent_ifr  ${RESTRICTED_CONTENT}
  Save form
  Log  \t\t\tCreat el document  console=True

Create a public document
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.document
  Input Text  name=form.widgets.title  ${PUBLIC_DOCUMENT_NAME}
  Input F_Textarea  form-widgets-defaultContent_ifr  ${PUBLIC_CONTENT}
  Save form
  Log  \t\t\tCreat el document públic  console=True

Create a restricted document
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.document
  Input Text  name=form.widgets.title  ${RESTRICTED_DOCUMENT_NAME}
  Input F_Textarea  form-widgets-alternateContent_ifr  ${RESTRICTED_CONTENT}
  Save form
  Log  \t\t\tCreat el document restringit  console=True

Create a file
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.file
  Input Text  name=form.widgets.title  ${FILE_NAME}
  Input File  form.widgets.visiblefile  ${PUBLIC_FILE_PATH}
  Input File  form.widgets.hiddenfile  ${RESTRICTED_FILE_PATH}
  Save form
  Log  \t\t\tCreat el fitxer  console=True

Create a public file
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.file
  Input Text  name=form.widgets.title  ${PUBLIC_FILE_NAME}
  Input File  form.widgets.visiblefile  ${PUBLIC_FILE_PATH}
  Save form
  Log  \t\t\tCreat el fitxer públic  console=True

Create a restricted file
  [Arguments]  ${URL}
  Go To  ${URL}/++add++genweb.organs.file
  Input Text  name=form.widgets.title  ${RESTRICTED_FILE_NAME}
  Input File  form.widgets.hiddenfile  ${RESTRICTED_FILE_PATH}
  Save form
  Log  \t\t\tCreat el fitxer restringit  console=True

Create a different contents
  Create a session  ${OG_URL}
  Create a agreement  ${SESSION_URL}
  Create a act  ${SESSION_URL}
  Create a point  ${SESSION_URL}
  Create a subpoint  ${POINT_URL}
  Create a document  ${POINT_URL}
  Create a public document  ${POINT_URL}
  Create a restricted document  ${POINT_URL}
  Create a file  ${POINT_URL}
  Create a public file  ${POINT_URL}
  Create a restricted file  ${POINT_URL}

Create a different users
  Create a OG secretary user
  Create a OG editor user
  Create a OG member user
  Create a OG affected user
  Create a validated user

Create a OG secretary user
  Create user OG  ${SECRETARY_USER_NAME}  OG1-Secretari
  Log  Creat l'usuari ${SECRETARY_USER_NAME}  console=True

Create a OG editor user
  Create user OG  ${EDITOR_USER_NAME}  OG2-Editor
  Log  Creat l'usuari ${EDITOR_USER_NAME}  console=True

Create a OG member user
  Create user OG  ${MEMBER_USER_NAME}  OG3-Membre
  Log  Creat l'usuari ${MEMBER_USER_NAME}  console=True

Create a OG affected user
  Create user OG  ${AFFECTED_USER_NAME}  OG4-Afectat
  Log  Creat l'usuari ${AFFECTED_USER_NAME}  console=True

Create a validated user
  Create user OG  ${VALIDATED_USER_NAME}
  Log  Creat l'usuari ${VALIDATED_USER_NAME}  console=True
