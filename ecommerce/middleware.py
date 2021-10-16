import traceback

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from ecommerce.models import Cart


class CartIdentifierMiddleWare(MiddlewareMixin):

    def process_request(self, request: HttpRequest):
        if not request.session.get('cart_id', None):
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.identifier.__str__()
        else:
            print(request.session.get('cart_id', None))

        if request.user.is_authenticated:
            try:
                existing_cart = request.user.profile.cart
                session_cart = Cart.objects.filter(identifier=request.session.get('cart_id')).first()
                if session_cart.lines.count() > 0:
                    session_cart.lines.update(cart=existing_cart)
            except Exception as e:
                traceback.print_exc()
                profile = request.user.profile
                cart = Cart.objects.filter(identifier=request.session.get('cart_id')).first()
                profile.cart = cart
                profile.save()
