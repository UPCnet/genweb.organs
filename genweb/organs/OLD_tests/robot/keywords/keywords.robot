*** Settings ***

Library  Selenium2Library
Library  Collections


*** Keywords ***

Open homepage
  Go to  ${PLONE_URL}

Go to login page
  Go to  ${PLONE_URL}/login_form

Login
  [Arguments]  ${USER}  ${PASSWORD}
  Logout
  Go to login page
  Click Element  xpath=//*[@id="accordionLogin"]/div[2]/div[1]/a
  Input Text  inputEmail  ${USER}
  Input Password  inputPassword  ${PASSWORD}
  Click Button  submit

Login as admin
  Login  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Logout
  Go to  ${PLONE_URL}/cas_logout

the default directories have been created
  Go to  ${PLONE_URL}/folder_contents
  Click Element  xpath=//*[@id="viewlet-above-content"]/div/a
  Click Button  name=createn3
  Log  Creat LRF  console=true

Confirm action
  ${BTN} =  Set Variable  name=form.button.confirm
  :FOR    ${LOOP}    IN RANGE    5
  \  ${STATUS} =  Run Keyword And Return Status  Page Should Contain Element  ${BTN}
  \  Run Keyword If  ${STATUS}  Click Button  ${BTN}
  \  ...  ELSE  Exit For Loop
  \  Run Keyword If  ${LOOP} > 2  Fatal Error
  \  ...  msg="There are problems with form button confirm. He asks for it more than once."

Save form
  ${STATUS} =  Run Keyword And Return Status
  ...  Page Should Contain Element	name=form.buttons.save
  Run Keyword If  ${STATUS}
  ...  Click Button  name=form.buttons.save
  ...  ELSE
  ...  Click Button  name=form.actions.save

Input F_Textarea
  [Arguments]  ${IFRAME}  ${TEXT}
  Wait Until Element Is Visible  id=${IFRAME}
  Select frame  id=${IFRAME}
  Input text  content  ${TEXT}
  Unselect frame

Input Textarea
  [Arguments]  ${FIELD}  ${TEXT}
  Wait Until Element Is Visible  name=${FIELD}
  Input text  name=${FIELD}  ${TEXT}

Input File
  [Arguments]  ${INPUT}  ${PATH}
  Choose File  name=${INPUT}  ${PATH}

Create a simple element
  [Arguments]  ${URL}  ${NAME}
  Go To  ${URL}
  Input Text  name=form.widgets.title  ${NAME}
  Save form

Status has been passed to public
  [Arguments]  ${URL}
  Go to  ${URL}
  Click Element  id=plone-contentmenu-workflow
  Click Element  id=workflow-transition-publish
  Confirm action
