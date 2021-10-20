import re


def is_mobile(request):
    """Return True if the request comes from a mobile device."""

    mobile_agent_re = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if mobile_agent_re.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False
