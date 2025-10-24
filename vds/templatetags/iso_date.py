from django import template

register = template.Library()


@register.filter(name='iso')
def iso(value):
    """Return ISO 8601 representation for date/datetime-like objects.

    If value is falsy (None/empty), returns an empty string so templates
    render gracefully.
    """
    if not value:
        return ""
    try:
        # Prefer isoformat if available (datetime/date)
        return value.isoformat()
    except Exception:
        # Fallback to string conversion
        return str(value)


@register.filter(name='iso_date')
def iso_date(value):
    """Return ISO date (YYYY-MM-DD) for date/datetime-like objects.

    For datetimes, it uses the date() portion.
    """
    if not value:
        return ""
    try:
        # datetime has date(); date has isoformat
        if hasattr(value, 'date'):
            return value.date().isoformat()
        return value.isoformat()
    except Exception:
        return str(value)
