#!/var/plone/python2.7/bin/python
#
# The Python Imaging Library.
# $Id$
#
# print image files to postscript printer
#
# History:
# 0.1   1996-04-20 fl   Created
# 0.2   1996-10-04 fl   Use draft mode when converting.
# 0.3   2003-05-06 fl   Fixed a typo or two.
#

from __future__ import print_function

VERSION = "pilprint 0.3/2003-05-05"



import sys
sys.path[0:0] = [
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Plone-4.3.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Pillow-2.7.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.multilingual-2.0.5_upcnet-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contenttypes-1.1b5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.upc-2.52-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.robotframework-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_ride-1.5.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/watchdog-0.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_debuglibrary-0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testrunner-4.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.schema-4.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.i18n-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.configuration-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.component-3.9.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/setuptools-36.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/selenium-2.43.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotsuite-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_selenium2library-1.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework-2.8.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.uuid-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.testing-5.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.testing-4.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.globalrequest-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Babel-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PluggableAuthService-1.10.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PlonePAS-4.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MailHost-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFPlone-4.3.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFCore-2.2.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.dexteritytextindexer-2.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.stack-2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.core-4.8.49-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.grok-1.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.GenericSetup-1.7.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFQuickInstallerTool-3.0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pytz-2013b-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.versioningbehavior-1.2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.namedfile-2.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.relationfield-1.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.querystring-1.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.dexterity-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.querystring-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.dexterity-2.0.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.event-1.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentmenu-2.0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.relationfield-0.6.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.theme-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.contenttree-1.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.behavior-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.z3cform-0.7.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.registry-1.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneLanguageTool-3.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wicked-1.1.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.theming-1.1.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.openid-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.iterate-2.1.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.caching-1.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFPlacefulWorkflow-1.5.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pathtools-0.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/argh-0.26.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/PyYAML-3.12-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.interface-3.6.7-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.exceptions-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.event-3.5.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.i18nmessageid-3.5.3-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/unittest2-0.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/lxml-2.3.6-py2.7-linux-x86_64.egg',
  '/home/roberto/.local/lib/python2.7/site-packages',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/docutils-0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/decorator-3.4.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.publisher-3.12.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.lifecycleevent-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browserpage-3.12.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testing-3.9.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Zope2-2.13.23-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.memoize-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.localsitemanager-2.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.site-3.9.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.dottedname-3.4.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.globalrequest-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PluginRegistry-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDefault-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.i18n-2.0.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.session-3.5.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.sendmail-3.7.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.deferredimport-3.5.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Persistence-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/DocumentTemplate-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/DateTime-3.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Acquisition-2.13.9-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/AccessControl-3.0.11-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.traversing-3.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.tales-3.5.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.tal-3.5.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.structuredtext-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.pagetemplate-3.6.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.location-3.9.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.deprecation-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.container-3.11.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.locales-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.autoinclude-0.3.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/transaction-1.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plonetheme.sunburst-1.4.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plonetheme.classic-1.3.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.registry-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.protect-3.0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlets-2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlet.static-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlet.collection-2.1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.locking-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.intelligenttext-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.indexer-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.fieldsets-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.contentrules-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.browserlayer-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.batching-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.workflow-2.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.vocabularies-2.1.20-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.viewletmanager-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.uuid-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.users-1.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.upgrade-1.3.18-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.search-1.1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.redirector-1.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.portlets-2.5.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.locales-4.3.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.linkintegrity-1.5.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.layout-2.3.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.jquerytools-1.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.jquery-1.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.i18n-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.form-2.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.folder-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.discussion-2.2.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.customerize-1.2.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.controlpanel-2.3.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentrules-3.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentlisting-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.content-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.collection-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.blob-1.5.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.customerize-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/borg.localrole-3.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.referencebrowserwidget-2.5.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.querywidget-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZODB3-3.10.5-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.statusmessages-4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TinyMCE-1.3.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ResourceRegistries-2.2.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PortalTransforms-2.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PlacelessTranslationService-2.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PasswordResetTool-2.0.18-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MimetypesRegistry-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExternalEditor-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExtendedPathIndex-3.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DCWorkflow-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFUid-2.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFFormController-3.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFEditions-2.2.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDynamicViewFTI-4.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDiffTool-2.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFCalendar-2.2.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFActionIcons-2.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Archetypes-1.9.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ATContentTypes-2.1.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ExtensionClass-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.publication-3.12.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZSQLMethods-2.13.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.form-3.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.z3cform-0.8.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.supermodel-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.api-1.8.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.multilingual-2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.recaptcha-2.0a3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.recaptcha-2.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pfg.drafts-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.collage.ploneformgen-1.0a1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.pfg.dexterity-0.10.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.polls-1.6.2.upcnet-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.logosfooter-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.banners-1.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/upcnet.stats-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/upcnet.cas-1.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.windowZ-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Collage-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneFormGen-1.7.17-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneLDAP-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.packets-2.17-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.restapi-2.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipdb-0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/simplejson-2.5.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/elasticsearch-5.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/souper.plone-1.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pyquery-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/quintagroup.seoptimizer-99.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/jarn.jsi18n-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wildcard.foldercontents-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.tinymcetemplates-1.0b4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.workflowmanager-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.lockingbehavior-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.referenceablebehavior-0.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.schemaextender-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.controlpanel-1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.portlets-1.2.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.js-1.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.cdn-1.60-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.theme-2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.contentprovider-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.annotation-3.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.viewlet-1.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.view-2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.site-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.security-1.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.component-2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.annotation-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/martian-0.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.formlib-4.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.container-3.9.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/rwproperty-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.autoform-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.rfc822-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.security-3.7.4-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.formwidget.query-0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.intid-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.intid-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.intid-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.size-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.filerepresentation-3.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browser-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.synchronize-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.folder-1.0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.alterego-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.schemaeditor-1.3.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.namedfile-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.textfield-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.z3cform.datetimewidget-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.recurrence-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.datetime-1.3.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.event-1.3.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/icalendar-4.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.elephantvocabulary-0.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZCatalog-2.13.27-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DateRecurringIndex-2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browsermenu-3.9.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.relation-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.objpath-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.intid-3.7.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.autocomplete-1.2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/repoze.xmliter-0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.resourceeditor-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.resource-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.transformchain-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.subrequest-1.6.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/roman-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/diazo-1.0.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.openid-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.viewlet-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.zcmlhook-1.0b1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browserresource-3.10.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.cachepurging-1.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.caching-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_dateutil-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.proxy-3.6.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.contenttype-3.5.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.StandardCacheManagers-2.13.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PythonScripts-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MIMETools-2.13.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExternalMethod-2.13.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.BTreeFolder2-2.13.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testbrowser-3.11.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.sequencesort-3.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.ptresource-3.9.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.processlifetime-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zLOG-2.11.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zExceptions-2.13.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zdaemon-2.0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/tempstorage-2.12.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/initgroups-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZopeUndo-2.12.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZConfig-2.9.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/RestrictedPython-3.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Record-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZCTextIndex-2.13.5-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.OFSP-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/MultiMapping-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Missing-2.13.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.ramcache-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.formlib-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Unidecode-0.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.keyring-3.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.broken-3.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.buildout-2.11.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.monkeypatcher-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.componentvocabulary-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.SecureMailHost-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.contentmigration-2.1.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/feedparser-5.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.cachedescriptors-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.stringinterp-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.validation-2.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.scale-1.3.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.imaging-1.0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.lockfile-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.content-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.outputfilters-1.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Markdown-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_gettext-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZopeVersionControl-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.copy-3.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.form-4.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Marshall-2.1.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.datetime-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ATReferenceBrowserWidget-3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.error-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.authentication-3.7.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/norecaptcha-0.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DataGridField-1.9.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.directives.dexterity-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/anz.casclient-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/stripogram-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.js.jqueryui-1.10.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PythonField-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TemplateFields-1.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TALESField-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.LDAPUserFolder-2.27-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.LDAPMultiPlugins-1.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/PyJWT-1.6.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.rest-1.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipython-5.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/souper-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/cssselect-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/quintagroup.canonicalpath-0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.directives.form-2.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.z3cform.datagridfield-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pyScss-1.2.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.jbot-0.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.dublincore-3.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.copypastemove-3.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.keyreference-3.6.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.caching-2.0a1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/experimental.cssselect-0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_openid-2.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/mechanize-0.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.bforest-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_ldap-2.4.25-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/dataflake.fakeldap-2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pexpect-4.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pathlib2-2.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/backports.shutil_get_terminal_size-1.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Pygments-1.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/prompt_toolkit-1.0.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/traitlets-4.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/simplegeneric-0.8.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pickleshare-0.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/repoze.catalog-0.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/node.ext.zodb-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ptyprocess-0.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/scandir-1.7-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wcwidth-0.1.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipython_genutils-0.2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.index-3.6.4-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/node-0.9.18.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plumber-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/odict-1.6.2-py2.7.egg',
  ]


from PIL import Image
from PIL import PSDraw

letter = ( 1.0*72, 1.0*72, 7.5*72, 10.0*72 )

def description(file, image):
    import os
    title = os.path.splitext(os.path.split(file)[1])[0]
    format = " (%dx%d "
    if image.format:
        format = " (" + image.format + " %dx%d "
    return title + format % image.size + image.mode + ")"

import getopt, os, sys

if len(sys.argv) == 1:
    print("PIL Print 0.2a1/96-10-04 -- print image files")
    print("Usage: pilprint files...")
    print("Options:")
    print("  -c            colour printer (default is monochrome)")
    print("  -p            print via lpr (default is stdout)")
    print("  -P <printer>  same as -p but use given printer")
    sys.exit(1)

try:
    opt, argv = getopt.getopt(sys.argv[1:], "cdpP:")
except getopt.error as v:
    print(v)
    sys.exit(1)

printer = None # print to stdout
monochrome = 1 # reduce file size for most common case

for o, a in opt:
    if o == "-d":
        # debug: show available drivers
        Image.init()
        print(Image.ID)
        sys.exit(1)
    elif o == "-c":
        # colour printer
        monochrome = 0
    elif o == "-p":
        # default printer channel
        printer = "lpr"
    elif o == "-P":
        # printer channel
        printer = "lpr -P%s" % a

for file in argv:
    try:

        im = Image.open(file)

        title = description(file, im)

        if monochrome and im.mode not in ["1", "L"]:
            im.draft("L", im.size)
            im = im.convert("L")

        if printer:
            fp = os.popen(printer, "w")
        else:
            fp = sys.stdout

        ps = PSDraw.PSDraw(fp)

        ps.begin_document()
        ps.setfont("Helvetica-Narrow-Bold", 18)
        ps.text((letter[0], letter[3]+24), title)
        ps.setfont("Helvetica-Narrow-Bold", 8)
        ps.text((letter[0], letter[1]-30), VERSION)
        ps.image(letter, im)
        ps.end_document()

    except:
        print("cannot print image", end=' ')
        print("(%s:%s)" % (sys.exc_info()[0], sys.exc_info()[1]))
