from products.models import Product

def is_valid_add(cart):
    error_message = []
    try:
        cart['product']
    except:
        cart['product'] = None

    try:
        cart['quantity']
    except:
        cart['quantity'] = None

    if not cart['quantity']:
        return False

    if not cart['product']:
        return False
    else:
        product = Product.objects.filter(product_code=cart['product'], 
                                        is_available=True, 
                                        out_of_stock=False)
        if not product:
            return False
    return True