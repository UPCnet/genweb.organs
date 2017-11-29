*** Settings ***

Force Tags  wip-not_in_docs

Library  Selenium2Library
Library  Collections

Resource  plone/app/robotframework/selenium.robot
Resource  keywords/keywords.robot

Test Setup  Open browser  ${PLONE_URL}  chrome
Test Teardown  Close all browsers


*** Test Cases ***

Login
  Given we're logged in as admin
  Then Page should contain  Us heu identificat correctament

Create default directories
  Given we're logged in as admin
  When the default directories have been created
  Then we verify that everything has been created correctly

OrganGovern added in a LRF
  Given we're logged in as admin
  When OrganGovern added in a LRF
  Then folder language have OrganGovern


*** Keywords ***

we verify that everything has been created correctly
  Within the Home directory
  Within the Català directory
  Within the Español directory
  Within the English directory
  Within the Templates directory

Within the Home directory
  @{LIST_FOLDER_CONTENTS} =  Set Variable  Català  Español  English  Templates
  ...                        Plantilles
  Go to  ${PLONE_URL}/folder_contents
  :FOR  ${STRING}  IN  @{LIST_FOLDER_CONTENTS}
  \  Page should contain  ${STRING}


Within the Català directory
  @{LIST_CATALA_CONTENTS} =  Set Variable  Notícies  Esdeveniments  Banners
  ...                        Logos peu  Benvingut  Contacte personalitzat
  ...                        Fitxers compartits
  Go to  ${PLONE_URL}/ca/folder_contents
  :FOR  ${STRING}  IN  @{LIST_CATALA_CONTENTS}
  \  Page should contain  ${STRING}

Within the Español directory
  @{LIST_SPANISH_CONTENTS} =  Set Variable  Noticias  Eventos  Banners
  ...                         Logos pie  Bienvenido  Contacto personalizado
  ...                         Ficheros compartidos
  Go to  ${PLONE_URL}/es/folder_contents
  :FOR  ${STRING}  IN  @{LIST_SPANISH_CONTENTS}
  \  Page should contain  ${STRING}

Within the English directory
  @{LIST_ENGLISH_CONTENTS} =  Set Variable  News  Events  Banners  Footer Logos
  ...                         Welcome  Custom contact   Shared files
  Go to  ${PLONE_URL}/en/folder_contents
  :FOR  ${STRING}  IN  @{LIST_ENGLISH_CONTENTS}
  \  Page should contain  ${STRING}

Within the Templates directory
  @{LIST_TEMPLATES_CONTENTS_1} =  Set Variable  Llistat índex  Llistat enllaços
  ...                             Llistat destacat  Text amb tots els titulars
  ...                             Dues columnes de text
  ...                             Combinacions de columnes  Columna de suport
  ...                             Destacat  Destacat color  Destacat contorn
  ...                             Pou  Pou degradat  Caixa  Caixa degradat
  ...                             Taula  Taula colors destacats
  ...                             Taula de registres per files
  ...                             Taula amb estils  Taula amb files destacades
  ...                             Calendari
  @{LIST_TEMPLATES_CONTENTS_2} =  Set Variable  Fitxa  Àlbum de fotografies
  ...                             Imatge alineada a l'esquerra amb text
  ...                             Imatge alineada a la dreta amb text
  ...                             Imatge amb text lateral superposat
  ...                             Assenyalar enllaços  Carousel d'imatges
  ...                             Pestanyes  Pestanyes caixa  Acordió
  ...                             Zoom imatge
  Go to  ${PLONE_URL}/templates/folder_contents
  :FOR  ${STRING}  IN  @{LIST_TEMPLATES_CONTENTS_1}
  \  Page should contain  ${STRING}
  Click Element  xpath=//*[@id="folderlisting-main-table-noplonedrag"]/div[1]/ul/a
  ${LOADING_PAGE} =  Get From List  ${LIST_TEMPLATES_CONTENTS_2}  0
  Wait Until Page Contains  ${LOADING_PAGE}
  :FOR  ${STRING}  IN  @{LIST_TEMPLATES_CONTENTS_2}
  \  Page should contain  ${STRING}

folder language have OrganGovern
  Go to  ${PLONE_URL}/ca/folder_contents
  Click Element  id=plone-contentmenu-factories
  Page should contain  Òrgan de govern
