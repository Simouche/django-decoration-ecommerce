import re

from ecommerce.models import DeliveryCompany, Settings, DeliveryFee


def is_mobile(request):
    """Return True if the request comes from a mobile device."""

    mobile_agent_re = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if mobile_agent_re.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


def calculate_delivery_fee_util(city, lines):
    delivery_company = DeliveryCompany.objects.get(default=True)
    settings = Settings.objects.all().first()

    try:
        base_fee = DeliveryFee.objects.get(state=city.state_id, company=delivery_company).fee
    except:
        base_fee = settings.standard_delivery_fee

    total_weight = 0
    for line in lines:
        total_weight += line.product.weight

    extra_weight = total_weight - delivery_company.weight_threshold
    if extra_weight > 0:
        fee = base_fee + (extra_weight * delivery_company.base_fee)
    else:
        fee = base_fee

    return fee
