import datetime
from DateTime import DateTime


def list_organs_by_review_state(catalog):
    filters = dict(
        portal_type='genweb.organs.organgovern')
    return catalog.searchResults(filters)


def datetime_to_DateTime(obj):
    return DateTime(
        obj.year, obj.month, obj.day,
        obj.hour, obj.minute, obj.second)


def get_date_range(delta, date_source=None):
    """
    Get a list representing the range of dates between now and now + delta.
    :param delta: Number of days behind/ahead the source date. If < 0,
    range is [source + delta, source], else [source, source + delta]
    :param date_source: datetime.datetime to which delta is applied.
    :return: 2-DateTime.DateTime element list representing the date range.
    """
    date_now = date_source if date_source else datetime.datetime.now()
    date_delta = date_now + datetime.timedelta(days=delta)
    datetime_now = datetime_to_DateTime(date_now)
    datetime_delta = datetime_to_DateTime(date_delta)
    return sorted([datetime_now, datetime_delta])


def list_sessions_by_delta_and_review_state(
        catalog, delta=None, review_state=None):
    filters = dict(
        portal_type='genweb.organs.sessio')
    if delta:
        filters['start'] = {
            'query': get_date_range(delta),
            'range': 'min:max'}
    if review_state:
        filters['review_state'] = review_state
    return catalog.searchResults(filters)


def list_acords_by_estat_aprovacio_and_delta_and_review_state(
        catalog, estat_aprovacio, delta=None, review_state=None):
    filters = dict(
        portal_type='genweb.organs.acord')
    if delta:
        filters['created'] = {
            'query': get_date_range(delta),
            'range': 'min:max'}
    if review_state:
        filters['review_state'] = review_state
    #We search for every object if its approved (you cant know it just with the brain, because its a field)
    results = []
    brains = catalog.searchResults(filters)
    for brain in brains:
        obj = brain.getObject()
        if obj.estatsLlista == 'Aprovat':
            results.append(obj)

    return results
