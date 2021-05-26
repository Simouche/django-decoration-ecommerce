from django.utils.deprecation import MiddlewareMixin

from ecommerce.models import Cart


class CartIdentifierMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        if not request.session.get('cart_id', None):
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.identifier.__str__()

        if request.user.is_authenticated:
            try:
                request.user.profile.cart
            except Exception:
                profile = request.user.profile
                profile.cart = Cart.objects.get(identifier=request.session.get('cart_id'))
                profile.save()
