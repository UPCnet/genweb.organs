# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote_plus
from Products.ZCTextIndex.ParseTree import ParseError
from ZTUtils import make_query

from five import grok
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from operator import itemgetter
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.publisher.browser import BrowserView

from genweb.core.utils import pref_lang
from genweb.organs import permissions
from genweb.organs.interfaces import IGenwebOrgansLayer

import json
import pkg_resources
# import time
# start_time = time.time()
# print("--- %s seconds --- " % (time.time() - start_time))

PLMF = MessageFactory('plonelocales')
_ = MessageFactory('plone')

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
MULTISPACE = u'\u3000'.encode('utf-8')
EVER = DateTime('1970/01/03')


def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s


class Search(BrowserView):

    def isAnon(self):
        if api.user.is_anonymous():
            return True

    def getOwnOrgans(self):
        if not api.user.is_anonymous():
            results = []
            portal_catalog = getToolByName(self, 'portal_catalog')
            root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
            lt = getToolByName(self, 'portal_languages')
            lang = lt.getPreferredLanguage()
            values = portal_catalog.searchResults(
                portal_type=['genweb.organs.organgovern'],
                path=root_path + '/' + lang)
            username = api.user.get_current().id
            for obj in values:
                organ = obj.getObject()
                all_roles = api.user.get_roles(username=username, obj=organ)
                roles = [o for o in all_roles if o in ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat']]
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                    results.append(dict(
                        url=obj.getObject().absolute_url(),
                        title=obj.Title,
                        color=organ.eventsColor,
                        role=roles))

            return results

    valid_keys = ('sort_on', 'sort_order', 'sort_limit', 'fq', 'fl', 'facet')

    def results(self, query=None, batch=True, b_size=100, b_start=0, old=False):
        """ Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' should be a dictionary of catalog parameters.
        """
        if batch:
            query['b_start'] = b_start = int(b_start)
            query['b_size'] = b_size
        query = self.filter_query(query)
        if query['path'] == '/empty_path/':
            return {}
        query['sort_order'] = 'reverse'
        newresults = []
        new_path = []
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        query_paths = [
            root_path + '/' + lang + '/consell-de-govern/consell-de-govern/',
            root_path + '/' + lang + '/cs/ple-del-consell-social/',
            root_path + '/' + lang + '/claustre-universitari/claustre-universitari/']

        username = api.user.get_current().id

        if root_path + '/not_anon_my_organs/' in query['path']:
            # Si no es anonim i ha enviat el check de "organs relacionats amb mi"
            # fem una cerca especial, amb un string que després eliminem
            if not api.user.is_anonymous():
                results = []
                values = api.content.find(
                    portal_type=['genweb.organs.organgovern'],
                    path=root_path + '/' + lang)
                for obj in values:
                    organ = obj.getObject()
                    all_roles = api.user.get_roles(username=username, obj=organ)
                    roles = [o for o in all_roles if o in ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat']]
                    sessionpath = obj.getPath()
                    if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                        if type(query['path']) == str:
                            query['path'] = sessionpath.split()
                        else:
                            query['path'].append(sessionpath)

        elif type(query['path']) == str:
            if query['path'] not in query_paths:
                return None
        else:
            for value in query['path']:
                if value not in query_paths:
                    return None

        if query['latest_session']:
            if isinstance(query['path'], list):
                for organ in query['path']:
                    session_path = api.content.find(
                        path=organ,
                        portal_type='genweb.organs.sessio',
                        sort_on='created',
                        sort_order='reverse')
                    if session_path:
                        new_path.append(session_path[0].getPath())
            if isinstance(query['path'], str):
                session_path = api.content.find(
                    path=query['path'],
                    portal_type='genweb.organs.sessio',
                    sort_on='created',
                    sort_order='reverse')
                if session_path:
                    new_path.append(session_path[0].getPath())
            query['path'] = new_path
        # Make default view return 0 results
        if 'SearchableText' not in query:
            # La primera vez, sin seleccionar nada, están marcados todos los elementos
            # Hacemos el check con el Folder
            if 'Folder' in query['portal_type']:
                return None
        if 'genweb.organs.punt' in query['portal_type']:
            query['portal_type'].append('genweb.organs.subpunt')
        if query is None:
            return None
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            try:
                #for all acords or punts
                results = catalog(**query)
                all_results= []
                for res in results:
                    all_results.append(res)

                #for subjects
                aux_subject_res = catalog.searchResults(portal_type=query['portal_type'], Subject=query['SearchableText'].replace('*', ''))
                for res in aux_subject_res:
                    if res not in all_results:
                        all_results.append(res)

                #for documents
                ptype = query['portal_type']
                query_docs = query
                query_docs['portal_type'] = "genweb.organs.document"
                aux_doc_res = catalog(**query_docs)
                for res in aux_doc_res:
                    obj = res.getObject()
                    parent = obj.getParentNode()
                    if parent.portal_type in ptype:
                        if parent not in all_results:
                            p_brain = catalog.searchResults(portal_type=ptype, id=parent.id)[0]
                            all_results.append(p_brain)

                for res in all_results:
                    item = res.getObject()
                    if item.portal_type == "genweb.organs.document":
                        item = item.getParentNode()

                    if item.portal_type == 'genweb.organs.punt':
                        if permissions.canViewPunt(self, item):
                            newresults.append(res)
                    if item.portal_type == 'genweb.organs.subpunt':
                        if permissions.canViewSubpunt(self, item):
                            newresults.append(res)
                    if item.portal_type == 'genweb.organs.acord':
                        if permissions.canViewAcord(self, item):
                            newresults.append(res)
            except ParseError:
                return []

        # Old documents
        if old:

            genweborgansegg = pkg_resources.get_distribution('genweb.organs')
            docs_1315 = open('{}/genweb/organs/2013-2015.json'.format(genweborgansegg.location))
            docs_9613 = open('{}/genweb/organs/1996-2013.json'.format(genweborgansegg.location))
            data = json.loads(docs_1315.read())
            data2 = json.loads(docs_9613.read())

            old_results = []
            for d in data:
                if query['SearchableText'].replace('*', '') in d['title']:
                    if isinstance(query['path'], str):
                        if str(d['unitat']).lower().replace(' ', '-') in query['path']:
                            old_results.append(d)
                    else:
                        for path in query['path']:
                            if str(d['unitat']).lower().replace(' ', '-') in path:
                                old_results.append(d)

            for d in data2:
                if query['SearchableText'].replace('*', '') in str(d['text']):
                    old_results.append(d)

            if batch:
                old_results = Batch(old_results, b_size, b_start)

            if 'created' not in query:
                return old_results
            else:
                return []

        results = IContentListing(newresults)

        if batch:
            results = Batch(results, b_size, b_start)

        return results

    def filter_query(self, query):
        request = self.request

        catalog = getToolByName(self.context, 'portal_catalog')
        valid_indexes = tuple(catalog.indexes())
        valid_keys = self.valid_keys + valid_indexes
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
            text = text + '*'  # Adding autocomplete words...
        if not text:
            # Without text, must provide a meaningful non-empty search
            valid = set(valid_indexes).intersection(request.form.keys()) or \
                set(valid_indexes).intersection(query.keys())
            if not valid:
                return

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):
                query[k] = v
        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        # Add new prperty to check if they are searching in latest session
        query['latest_session'] = False
        if created:
            if created['query'][0].ISO() == '1900-11-12T00:00:00':  # Fake to simulate LAST_SESSION
                # Search latest session bassed on params
                query['latest_session'] = True
            else:
                try:
                    if created.get('query') and created['query'][0] <= EVER:
                        del query['created']
                except AttributeError:
                    # created not a mapping
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            # Added /Plone/ca
            # query['path'] = '/all_checked/'
            # getNavigationRoot(self.context)
            # Added all defaults folders:
            if 'genweb.organs.acord' or 'genweb.organs.punt' in query['portal_type']:
                query['path'] = '/empty_path/'
            else:
                root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
                lt = getToolByName(self, 'portal_languages')
                lang = lt.getPreferredLanguage()
                query['path'] = [
                    root_path + '/' + lang + '/consell-de-govern/consell-de-govern/',
                    root_path + '/' + lang + '/cs/ple-del-consell-social/',
                    root_path + '/' + lang + '/claustre-universitari/claustre-universitari/']
        return query

    def filter_types(self, types):
        plone_utils = getToolByName(self.context, 'plone_utils')
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)

    def types_list(self):
        # only show the types of Organs de Govern
        # removed subpunt because visually is the same that punt.
        # Subpunt is added in other part of code
        # catalog = getToolByName(self.context, 'portal_catalog')
        # used_types = catalog._catalog.getIndex('portal_type').uniqueValues()
        used_types = ('genweb.organs.acord', 'genweb.organs.punt')
        return sorted(self.filter_types(list(used_types)))

    def getLatestCDG(self):
        """ Retorna ultima sessió consell de govern en estat que no sigui planificada """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/consell-de-govern/consell-de-govern",
            sort_on='created',
            sort_order='reverse')

        if items:
            results = []
            for item in items:
                itemObj = item._unrestrictedGetObject()
                estatSessio = api.content.get_state(obj=itemObj)
                if estatSessio != 'planificada':
                    num = itemObj.numSessio.zfill(3)
                    any = itemObj.start.strftime('%Y%m%d')
                    results.append(dict(title=item.Title,
                                        url=itemObj.absolute_url(),
                                        hiddenOrder=int(any + num)))
            if results:
                results = sorted(results, key=itemgetter('hiddenOrder'), reverse=True)
                title = results[0]['title']
                url = results[0]['url']
                return dict(title=title, url=url)

    def getLatestCS(self):
        """ Retorna ultima sessió consell social en estat que no sigui planificada """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/cs/ple-del-consell-social",
            sort_on='created',
            sort_order='reverse')

        if items:
            results = []
            for item in items:
                itemObj = item._unrestrictedGetObject()
                estatSessio = api.content.get_state(obj=itemObj)
                if estatSessio != 'planificada':
                    num = itemObj.numSessio.zfill(3)
                    any = itemObj.start.strftime('%Y%m%d')
                    results.append(dict(title=item.Title,
                                        url=itemObj.absolute_url(),
                                        hiddenOrder=int(any + num)))
            if results:
                results = sorted(results, key=itemgetter('hiddenOrder'), reverse=True)
                title = results[0]['title']
                url = results[0]['url']
                return dict(title=title, url=url)

    def getLatestCU(self):
        """ Retorna ultima sessió claustre universitari en estat que no sigui planificada """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/claustre-universitari/claustre-universitari",
            sort_on='created',
            sort_order='reverse')

        if items:
            results = []
            for item in items:
                itemObj = item._unrestrictedGetObject()
                estatSessio = api.content.get_state(obj=itemObj)
                if estatSessio != 'planificada':
                    num = itemObj.numSessio.zfill(3)
                    any = itemObj.start.strftime('%Y%m%d')
                    results.append(dict(title=item.Title,
                                        url=itemObj.absolute_url(),
                                        hiddenOrder=int(any + num)))
            if results:
                results = sorted(results, key=itemgetter('hiddenOrder'), reverse=True)
                title = results[0]['title']
                url = results[0]['url']
                return dict(title=title, url=url)

    def sort_options(self):
        """ Sorting options for search results view. """
        return (
            SortOption(
                self.request, _(u'date (newest first)'),
                'Date', reverse=True
            ),
            SortOption(self.request, _(u'alphabetically'), 'sortable_title'),
        )

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]
        # Fixed to Remove Unit OG Folder Name
        breadcrumbs = breadcrumbs[1:]
        if len(breadcrumbs) == 0:
            # don't show breadcrumbs if we only have a single element
            return None
        if len(breadcrumbs) > 3:
            # if we have too long breadcrumbs, emit the middle elements
            empty = {'absolute_url': '', 'Title': unicode('…', 'utf-8')}
            breadcrumbs = [breadcrumbs[0], empty] + breadcrumbs[-2:]
        return breadcrumbs

    def navroot_url(self):
        if not hasattr(self, '_navroot_url'):
            state = self.context.unrestrictedTraverse('@@plone_portal_state')
            self._navroot_url = state.navigation_root_url()
        return self._navroot_url

    def root_path(self):
        path = '/'.join(api.portal.get().getPhysicalPath())
        return path

    def getPage(self):
        """ Retorna la pagina benvingut """
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['Document'], id='benvingut')
        if item:
            return item[0].getObject().text.output


class SortOption(object):

    def __init__(self, request, title, sortkey='', reverse=False):
        self.request = request
        self.title = title
        self.sortkey = sortkey
        self.reverse = reverse

    def selected(self):
        sort_on = self.request.get('sort_on', '')
        return sort_on == self.sortkey

    def url(self):
        q = {}
        q.update(self.request.form)
        if 'sort_on' in q.keys():
            del q['sort_on']
        if 'sort_order' in q.keys():
            del q['sort_order']
        q['sort_on'] = self.sortkey
        if self.reverse:
            q['sort_order'] = 'reverse'

        base_url = self.request.URL
        # After the AJAX call the request is changed and thus the URL part of
        # it as well. In this case we need to tweak the URL to point to have
        # correct URLs
        if '@@updated_search' in base_url:
            base_url = base_url.replace('@@updated_search', '@@search')
        return base_url + '?' + make_query(q)


# Hide show more
class TypeAheadSearch(grok.View):
    grok.name('gw_type_ahead_search')
    grok.context(Interface)
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        # We set the parameters sent in livesearch using the old way.
        q = self.request['q']

        limit = 10
        path = None
        ploneUtils = getToolByName(self.context, 'plone_utils')
        portal_url = getToolByName(self.context, 'portal_url')()
        pretty_title_or_id = ploneUtils.pretty_title_or_id
        portalProperties = getToolByName(self.context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        # SIMPLE CONFIGURATION
        MAX_TITLE = 40
        MAX_DESCRIPTION = 80

        # generate a result set for the query
        catalog = self.context.portal_catalog

        friendly_types = ploneUtils.getUserFriendlyTypes()

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_bad_chars(r) + '*'
        searchterms = url_quote_plus(r)

        params = {'SearchableText': r,
                  'portal_type': friendly_types,
                  'sort_limit': limit + 1}

        if path is None:
            # useful for subsides
            params['path'] = getNavigationRoot(self.context)
        else:
            params['path'] = path

        params["Language"] = pref_lang()
        # search limit+1 results to know if limit is exceeded
        results = catalog(**params)

        REQUEST = self.context.REQUEST
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', 'application/json')

        label_show_all = _('label_show_all', default='Show all items')

        ts = getToolByName(self.context, 'translation_service')

        queryElements = []

        if results:
            # TODO: We have to build a JSON with the desired parameters.
            for result in results[:limit]:
                # Calculate icon replacing '.' per '-' as '.' in portal_types break CSS
                icon = result.portal_type.lower().replace(".", "-")
                itemUrl = result.getURL()
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                full_title = safe_unicode(pretty_title_or_id(result))
                if len(full_title) > MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE], '...'))
                else:
                    display_title = full_title

                full_title = full_title.replace('"', '&quot;')

                display_description = safe_unicode(result.Description)
                if len(display_description) > MAX_DESCRIPTION:
                    display_description = ''.join(
                        (display_description[:MAX_DESCRIPTION], '...'))

                # We build the dictionary element with the desired parameters and we add it to the queryElements array.
                queryElement = {
                    'class': '',
                    'title': display_title,
                    'description': display_description,
                    'itemUrl': itemUrl,
                    'icon': icon}
                queryElements.append(queryElement)

        return json.dumps(queryElements)
