from django.shortcuts import render
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum, F
from rest_framework.response import Response

from base.tasks import is_authenticated
from products.models import Product
from orders.models import Cart, Order, OrderLine, Payment
from orders.apis import is_valid_add
from orders.forms import PaymentForm
from orders.commons import ORDER_STATUS, PAYMENT_STATUS

import logging
logger = logging.getLogger(__name__)


class CartDetailView(APIView):
    def get(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        user_cart = Cart.objects.filter(user=authenticated_result, is_checkout=False)
        total_price = user_cart.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or "Cart is empty"

        cart_list = []
        for cart in user_cart:
            cart_list.append({
                "id":cart.id,
                "product":cart.product,
                "quantity":cart.quantity,
            })
        return Response({"User_cart": cart_list, "Total_price": total_price}, status=200)


class AddToShoppingCartView(APIView):
    def post(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        try:
            full_data = self.request.data
        except:
            return Response([{"Error_message" : "None data"}])

        try:
            cart = full_data["cart"]
        except:
            return Response([{"Error_message" : "Wrong data type"}])

        if not is_valid_add(cart):
            return Response({"Error_message" : "Wrong data type"})

        # get product's instance
        product_instance = Product.objects.filter(product_code=cart['product'])

        added_cart = Cart.objects.update_or_create(user=authenticated_result, 
                                                    product=product_instance,
                                                    defaults={'quantity':cart['quantity']})

        if not added_cart:
            return Response({"Error" : "Failed to update or create new cart"}, status=500)
        else:
            return Response({"Products": added_cart.product.product_code,
                            "Quantity":added_cart.quantity}, status=200)


class UpdataCartView(APIView):
    def put(self,request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)

        data = self.request.data
        update_cart = data['cart']
        try:
            update_cart['product']
        except:
            return Response({"Error":"Shopping cart's product does not exist"})
        try:
            update_cart['quantity']
        except:
            return Response({"Error":"Product's quantity does not exist"}, status=400)
        
        exist_cart = Cart.objects.filter(user=authenticated_result, 
                                        product__product_code=update_cart['product'])

        stocks = Product.objects.filter(product_code=update_cart['product'],
                                        out_of_stock=False, is_available=True)

        if not exist_cart:
            return Response({"Error":"Shopping cart does not exist"}, status=404)

        if not stocks:
            return Response({"Error":"Product does not exist"}, status=410)
        
        update_quantity = int(exist_cart.first().quantity) + update_cart['quantity']

        if update_quantity <= 0:
            exist_cart.first().delete()
        else:
            update_count = exist_cart.update(quantity=update_quantity)

        if update_count == 0:
            return Response({"Error" : "Falied to update shopping cart"}, status=500)
        else:
            updated_cart = Cart.objects.filter(user=authenticated_result, 
                                                product__product_code=update_cart['product']).first()

            if updated_cart.quantity == stocks.first().quantity:
                # feedback to frontend that the amount of product has reached the maximum
                return Response({"Products": updated_cart.product.product_code,
                                "Quantity":updated_cart.quantity}, status=210)
            return Response({"Products": updated_cart.product.product_code,
                            "Quantity":updated_cart.quantity}, status=200)


"""
checkout process : 
1. products are in the shopping cart
2. user click checkout, then asked to fill out order information. 
   While user click checkout button that it will send info to backend.
3. After step 2. Paying process, which will return payment info to backend.
   Then create Payment, also update Cart and Order
"""
class CreateOrderView(APIView):
    def post(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        order_data = self.request.data

        cart_list = []
        for cart in data['cart']:
            if cart['id'] not in cart_list:
                cart_list.append(cart['id'])

        carts = Cart.objects.filter(id__in=cart_list, 
                                    user=authenticated_result, 
                                    has_order=False, 
                                    is_checkout=False
                                    ).order_by('id').distinct()
        if not carts:
            return Response({"Error":"Cart does not exist, hence failed to create new orderline"}, 
                            status=417)
        elif carts.count() != len(cart_list):
            return Response({"Error":"Cart's record does not match"}, error=400)

        cart_total_price = carts.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0

        for data in order_data:
            order = data['order']

            # check user's order history, if exist then cancel it
            previous_order = Order.objects.filter(user=authenticated_result, is_paid=False, order_status=ORDER_STATUS.SUBMIT)
            if previous_order:
                previous_order.update(order_status=ORDER_STATUS.CANCEL)

            # generate new order serial number
            now = timezone.now()
            document_no_prefix = now.strftime('%Y%m%d')
            serial_count = str(Order.objects.filter(order_serial_number__startswith=document_no_prefix).count() + 1)
            new_serial_number = document_no_prefix + serial_count.zfill(5)

            new_order = Order.objects.create(order_serial_number=new_serial_number,
                                            user=authenticated_result,
                                            receiver_name=order['receiver_name'],
                                            receiver_phone=order['receiver_phone'],
                                            shipping_address=order['shipping_address'],
                                            city=order['city'],
                                            post_code=order['post_code'],
                                            total_price=cart_total_price,
                                            comment=order['comment'],
                                            order_status=order['order_status'])
            if not new_order:
                return Response({"Error" : "Failed to create new order"}, status=500)
            else:
                base_line_no = 0
                line_list = []

                for cart in carts:
                    line_list.append(OrderLine(order=new_order,
                                    line_no=base_line_no + 1,
                                    product=cart.product.id,
                                    quantity=cart.quantity))

                if not line_list:
                    new_order.order_status=ORDER_STATUS.ERROR
                    new_order.save()
                    return Response({"Error":"Failed to ceate orderline object before bulk_create"}, 
                                    status=500)
                else:
                    new_line = OrderLine.objects.bulk_create(line_list)
                    if not new_line:
                        new_order.order_status=ORDER_STATUS.ERROR
                        new_order.save()
                        return Response({"Error":"Failed to create new orderline"}, status=500)
                    carts.update(has_order=True)
                    new_order.order_status = ORDER_STATUS.SUBMIT
                    new_order.save()

        return Response({"Order":{
                                "order_serial_number":new_order.order_serial_number or "",
                                "user":new_order.user.id or "",
                                "receiver_name":new_order.receiver_name or "",
                                "receiver_phone":new_order.receiver_phone or "",
                                "shipping_address":new_order.shipping_address or "",
                                "city":new_order.city or "",
                                "post_code":new_order.post_code or "",
                                "comment":new_order.comment or "",
                                "order_status":new_order.order_status or "",
                                "order_line":[
                                    {
                                    "order":line.order or "",
                                    "line_no":line.line_no or "",
                                    "product":line.product or "",
                                    "quantity":line.quantity or ""
                                    }for line in new_order.orderline_set.all().distinct()]
                                }
                                })


class CheckOutView(APIView):
    def post(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        checkout_cart = Cart.objects.filter(user=authenticated_result, has_order=True, 
                                            is_checkout=False).order_by('id')
        checkout_order = Order.objects.filter(user=authenticated_result, is_paid=False, order_status=ORDER_STATUS.SUBMIT)

        if not checkout_cart:
            return Response({"Error":"Cart does not exist, hence failed to checkout"}, status=417)

        if not checkout_order:
            return Response({"Error":"Order does not exist, hence failed to checkout"}, status=417)
        elif checkout_order.count() > 1:
            return Response({"Error":"The amount of order greater than one, hence failed to checkout"}, 
                                    status=417)
        
        data = self.request.data

        pay_info = data['payment']
        valid_pay = PaymentForm(pay_info)
        if not valid_pay.is_valid():
            return Response({"Error": "Missing field : %s" %valid_pay.errors.keys()}, status=400)

        paid = Payment.objects.create(user=authenticated_result,
                                    order=checkout_order.first(),
                                    pay_org=pay_info['pay_org'],
                                    card_last_number=pay_info['card_last_number'],
                                    payment_status=pay_info['payment_status'],
                                    total_price=pay_info['total_price'] or 0)

        if not paid:
            return Response({"Error" : "Failed to create payment"}, status=500)
        
        if paid.total_price == 0:
            paid.payment_status = PAYMENT_STATUS.FAILED
            paid.save()
            return Response({"Error" : "None receive payment"}, status=400)
        
        update_count = checkout_cart.update(payment=paid, is_checkout=True)
        if update_count != checkout_cart.count():
            return Response({"Error" : "Failed to update shopping cart's payment status"}, status=417)
        update_order = checkout_order.update(is_paid=True)
        if update_order != checkout_cart.count():
            return Response({"Error" : "Failed to update order's payment status"}, status=417)
        
        return Response({"Payment" : "Order : %s (order number) has been paid" %paid.order.order_serial_number}, 
                        status=200)