#|/bin/bash
EXCLUDE="bin build develop-eggs eggs include lib local parts"
cd ..
cd ..
cd ..
~/bin/i18ndude rebuild-pot --pot genweb/organs/locales/genweb.organs.pot --create genweb.organs . --exclude "$EXCLUDE"
cd genweb/organs/locales/ca/LC_MESSAGES
~/bin/i18ndude sync --pot ../../genweb.organs.pot genweb.organs.po
cd ..
cd ..
cd en
cd LC_MESSAGES
~/bin/i18ndude sync --pot ../../genweb.organs.pot genweb.organs.po
cd ..
cd ..
cd es
cd LC_MESSAGES
~/bin/i18ndude sync --pot ../../genweb.organs.pot genweb.organs.po
