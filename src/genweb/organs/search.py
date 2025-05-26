from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote_plus
from Products.ZCTextIndex.ParseTree import ParseError
from ZTUtils import make_query

from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from operator import itemgetter
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from Products.Five.browser import BrowserView

from genweb6.core.utils import pref_lang
from genweb.organs import permissions
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import utils

import json
import pkg_resources
# import time
# start_time = time.time()
# print("--- %s seconds --- " % (time.time() - start_time))

PLMF = MessageFactory('plonelocales')
_ = MessageFactory('plone')

# We should accept both a simple space, unicode '\u0020' but also a
# multi-space, so called 'waji-kankaku', unicode '\u3000'
MULTISPACE = '\u3000'
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
    """
    Vista de búsqueda para órganos, sesiones y acuerdos.
    Compatible con Plone 6 y el nuevo template search.pt (Bootstrap 5).
    """

    def getOwnOrgans(self):
        if api.user.is_anonymous():
            return []
        results = []
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        lang = api.portal.get_tool('portal_languages').getDefaultLanguage()
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.organgovern'],
            path=f'{root_path}/{lang}'
        )
        username = api.user.get_current().id
        for obj in values:
            organ = obj.getObject()
            all_roles = api.user.get_roles(username=username, obj=organ)
            roles = [o for o in all_roles if o in ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat']]
            if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                results.append(dict(
                    url=organ.absolute_url(),
                    title=obj.Title,
                    color=getattr(organ, 'eventsColor', '#007bc0'),
                    role=roles))
        return results

    def getLatestCDG(self):
        return self._getLatestSession('consell-de-govern/consell-de-govern', 'Consell de Govern')

    def getLatestCS(self):
        return self._getLatestSession('cs/ple-del-consell-social', 'Consell Social')

    def getLatestCU(self):
        return self._getLatestSession('claustre-universitari/claustre-universitari', 'Claustre Universitari')

    def _getLatestSession(self, rel_path, label):
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        lang = api.portal.get_tool('portal_languages').getDefaultLanguage()
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        items = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=f'{root_path}/{lang}/{rel_path}',
            sort_on='created',
            sort_order='reverse')
        for item in items:
            itemObj = item._unrestrictedGetObject()
            estatSessio = api.content.get_state(obj=itemObj)
            if estatSessio != 'planificada':
                return dict(title=item.Title, url=itemObj.absolute_url())
        return None

    def results(self, query=None, batch=True, b_size=100, b_start=0, old=False):
        if query is None:
            query = {}
        if not self.request.form and not query:
            return []
        if batch:
            query['b_start'] = b_start = int(b_start)
            query['b_size'] = b_size
        query = self.filter_query(query)
        if not query or query.get('path') == '/empty_path/':
            return []
        query['sort_order'] = 'reverse'
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        results = portal_catalog(**query)
        # Adaptar los resultados para el frontend Bootstrap
        output = []
        for res in results:
            obj = res.getObject()
            output.append({
                'Title': res.Title,
                'getURL': res.getURL(),
                'portal_type': res.portal_type,
                'created': getattr(res, 'created', ''),
            })
        return output

    def filter_query(self, query):
        # Solo filtra si hay texto o algún filtro
        request = self.request
        catalog = api.portal.get_tool(name='portal_catalog')
        valid_indexes = tuple(catalog.indexes())
        valid_keys = ('sort_on', 'sort_order', 'sort_limit', 'fq', 'fl', 'facet') + valid_indexes
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
        if not text and not any(k in request.form for k in ['portal_type', 'organ', 'period']):
            return {}
        # Construye el query
        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):
                query[k] = v
        if text:
            query['SearchableText'] = text + '*'
        # Tipos
        types = query.get('portal_type', [])
        if isinstance(types, str):
            types = [types]
        query['portal_type'] = types or ['genweb.organs.acord', 'genweb.organs.punt']
        # Path por defecto
        if 'path' not in query:
            root_path = '/'.join(api.portal.get().getPhysicalPath())
            lang = api.portal.get_tool('portal_languages').getDefaultLanguage()
            query['path'] = [
                f'{root_path}/{lang}/consell-de-govern/consell-de-govern/',
                f'{root_path}/{lang}/cs/ple-del-consell-social/',
                f'{root_path}/{lang}/claustre-universitari/claustre-universitari/'
            ]
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
        # catalog = api.portal.get_tool(name='portal_catalog')
        # used_types = catalog._catalog.getIndex('portal_type').uniqueValues()
        used_types = ('genweb.organs.acord', 'genweb.organs.punt')
        return sorted(self.filter_types(list(used_types)))

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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
class TypeAheadSearch(BrowserView):
    def __call__(self):
        return self.render()

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

        multispace = '\u3000'
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
