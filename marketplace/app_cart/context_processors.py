from .cart import Cart


def cart(request):
    cart = Cart(request)
    return {"cart": cart, "quantity": len(cart), "total_price": cart.get_total_price()}

