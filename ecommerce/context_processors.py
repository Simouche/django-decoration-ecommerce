from ecommerce.utils import is_mobile


def add_is_mobile(request):
    return {
        'is_mobile': is_mobile(request)
    }
