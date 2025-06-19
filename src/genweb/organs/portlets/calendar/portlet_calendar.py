from Acquisition import aq_inner
from ComputedAttribute import ComputedAttribute
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.contenttypes.interfaces import IFolder
from plone.app.event import _
from plone.app.event.base import _prepare_range
from plone.app.event.base import construct_calendar
from plone.app.event.base import expand_events
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events
from plone.app.event.base import localized_today
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import start_end_query
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.portlets.portlets import base
from plone.app.querystring import queryparser
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.event.interfaces import IEventAccessor
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope import schema
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from datetime import datetime
from plone import api
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor

import calendar
import json


search_base_uid_source = CatalogSource(
    object_provides={
        "query": [ISyndicatableCollection.__identifier__, IFolder.__identifier__],
        "operator": "or",
    }
)

PLMF = MessageFactory("plonelocales")


class ICalendarOrgansPortlet(IPortletDataProvider):
    """A portlet displaying a calendar"""

    state = schema.Tuple(
        title=_("Workflow state"),
        description=_("Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowStates"),
    )

    search_base_uid = schema.Choice(
        title=_("portlet_label_search_base", default="Search base"),
        description=_(
            "portlet_help_search_base",
            default="Select search base Folder or Collection to search for "
            "events. The URL to to this item will also be used to "
            "link to in calendar searches. If empty, the whole site "
            "will be searched and the event listing view will be "
            "called on the site root.",
        ),
        required=False,
        source=search_base_uid_source,
    )


@implementer(ICalendarOrgansPortlet)
class Assignment(base.Assignment):
    title = _(u'Organs Calendar')

    # reduce upgrade pain
    state = None

    def __init__(self, state=None, search_base_uid=None):
        self.state = state
        self.search_base_uid = search_base_uid

    def _uid(self):
        # This is only called if the instance doesn't have a search_base_uid
        # attribute, which is probably because it has an old
        # 'search_base' attribute that needs to be converted.
        path = self.search_base
        try:
            search_base = getSite().unrestrictedTraverse(path.lstrip("/"))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return search_base.UID()

    search_base_uid = ComputedAttribute(_uid, 1)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile("portlet_calendar.pt")
    _search_base = None

    @property
    def search_base(self):
        if not self._search_base and self.data.search_base_uid:
            self._search_base = uuidToObject(self.data.search_base_uid)
        return aq_inner(self._search_base) if self._search_base else None

    @property
    def search_base_path(self):
        return (
            "/".join(self.search_base.getPhysicalPath()) if self.search_base else None
        )  # noqa

    def update(self):
        context = aq_inner(self.context)

        self.calendar_url = get_calendar_url(context, self.search_base_path)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = (
            prev_year,
            prev_month,
        ) = self.get_previous_month(year, month)
        self.next_year, self.next_month = next_year, next_month = self.get_next_month(
            year, month
        )
        self.prev_query = f"?month={prev_month}&year={prev_year}"
        self.next_query = f"?month={next_month}&year={next_year}"

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, "translation_service")
        self.month_name = PLMF(
            self._ts.month_msgid(month), default=self._ts.month_english(month)
        )

        # strftime %w interprets 0 as Sunday unlike the calendar.
        strftime_wkdays = [wkday_to_mon1(day) for day in self.cal.iterweekdays()]
        self.weekdays = [
            PLMF(
                self._ts.day_msgid(day, format="s"),
                default=self._ts.weekday_english(day, format="a"),
            )
            for day in strftime_wkdays
        ]

    def year_month_display(self):
        """Return the year and month to display in the calendar."""
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from request
        year = request.get("year", None)
        month = request.get("month", None)

        # Or use current date
        today = localized_today(context)
        if not year:
            year = today.year
        if not month:
            month = today.month

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        return year, month

    def get_previous_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def get_next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def date_events_url(self, date):
        return f"{self.calendar_url}?mode=day&date={date}"

    def get_public_organs_fields(self):
        visibleItems = api.content.find(
            portal_type='genweb.organs.organgovern',
            visiblefields=True)
        items_path = []
        for obj in visibleItems:
            items_path.append(obj.getPath())
        return items_path

    def getclasstag_event(self, day):
        # Returns class color to render inside the calendar
        classtag = ''
        if day['events']:
            if len(day['events']) > 1:
                classtag += ' event-multiple '
        return classtag

    def getDateEvents(self):
        formatDate = "%Y-%m-%d"
        if 'day' in self.request.form:
            date = '{}-{}-{}'.format(
                self.request.form['year'],
                self.request.form['month'],
                self.request.form['day'])
        else:
            date = datetime.today().strftime(formatDate)
        dateEvent = datetime.strptime(date, formatDate)
        return dateEvent

    def getEventCalendarDict(self, event):
        eventhour = IEventAccessor(event)
        start = event.start.strftime('%d/%m')
        starthour = eventhour.start.strftime('%H:%M')
        end = event.end.strftime('%d/%m')
        endhour = eventhour.end.strftime('%H:%M')
        end = None if end == start else end
        return dict(title=event.title,
                    url=event.absolute_url(),
                    organ_title=event.aq_parent.title,
                    organ_url=event.aq_parent.absolute_url(),
                    start=start,
                    starthour=starthour,
                    end=end,
                    endhour=endhour,
                    color=event.aq_parent.eventsColor
                    )

    def filterOccurrenceEvents(self, events):
        filter_events = []
        for event in events:
            if not IEvent.providedBy(event):
                ocurrence = event
                event = event.aq_parent
                if event not in filter_events:
                    event.ocstart = ocurrence.start
                    event.ocend = ocurrence.end
                    filter_events.append(event)
            else:
                filter_events.append(event)

        return filter_events

    def getDayEventsGroup(self):
        request = self.request
        if 'day' in request.form:
            return self.getDayEvents(self.getDateEvents())  # Solo si hay día seleccionado
        else:
            # Lógica para mostrar todos los eventos del mes
            year, month = self.year_month_display()
            monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
            cal_dict = self.getCalendarDict()
            events_dict = {}  # Para evitar duplicados
            for dat in monthdates:
                isodat = dat.strftime('%Y-%m-%d')
                if isodat in cal_dict:
                    events = self.filterOccurrenceEvents(cal_dict[isodat])
                    for event in events:
                        if event.UID() not in events_dict:
                            events_dict[event.UID()] = self.getEventCalendarDict(event)
            results = list(events_dict.values())
            return results

    def getDayEvents(self, date):
        events = self.getCalendarDict()
        list_events = []
        if date.strftime('%Y-%m-%d') in events:
            events = self.filterOccurrenceEvents(events[date.strftime('%Y-%m-%d')])
            for event in events:
                list_events.append(self.getEventCalendarDict(event))
        return list_events

    def getCalendarDict(self):
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        start = monthdates[0]
        end = monthdates[-1]

        date_range_query = {'query': (start, end), 'range': 'min:max'}
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        events = []
        if api.user.is_anonymous():
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query,
                path=self.get_public_organs_fields())
            for event in items:
                events.append(event._unrestrictedGetObject())
        else:
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query)
            username = api.user.get_current().id
            for event in items:
                session = event._unrestrictedGetObject()
                roles = api.user.get_roles(username=username, obj=session)
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles or 'Manager' in roles or session.aq_parent.visiblefields:
                    events.append(session)

        return construct_calendar(events, start=start, end=end)

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        start = monthdates[0]
        end = monthdates[-1]

        date_range_query = {'query': (start, end), 'range': 'min:max'}
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        events = []
        if api.user.is_anonymous():
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query,
                path=self.get_public_organs_fields())
            for event in items:
                events.append(event._unrestrictedGetObject())
        else:
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query)
            username = api.user.get_current().id
            for event in items:
                session = event._unrestrictedGetObject()
                roles = api.user.get_roles(username=username, obj=session)
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles or 'Manager' in roles or session.aq_parent.visiblefields:
                    events.append(session)

        cal_dict = construct_calendar(events, start=start, end=end)

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            color = ''
            if date_events:
                for occ in date_events:
                    color = occ.aq_parent.eventsColor

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'month': dat.month,
                 'year': dat.year,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'color': color,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'events': date_events})
        return caldata

    def nav_pattern_options(self, year, month):
        val = self.hash
        if isinstance(val, bytes):
            val = val.decode("utf-8")

        return json.dumps(
            {
                "url": "%s/@@render-portlet?portlethash=%s&year=%s&month=%s"
                % (getSite().absolute_url(), val, year, month),
                "target": "#portletwrapper-%s > *" % val,
            }
        )

    @property
    def hash(self):
        return self.request.form.get(
            "portlethash", getattr(self, "__portlet_metadata__", {}).get("hash", "")
        )


class AddForm(base.AddForm):
    schema = ICalendarOrgansPortlet
    label = _("Add Calendar Portlet")
    description = _("This portlet displays events in a calendar.")

    def create(self, data):
        return Assignment(
            state=data.get("state", None),
            search_base_uid=data.get("search_base_uid", None),
        )


class EditForm(base.EditForm):
    schema = ICalendarOrgansPortlet
    label = _("Edit Calendar Portlet")
    description = _("This portlet displays events in a calendar.")
