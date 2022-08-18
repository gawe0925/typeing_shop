from itertools import product
from tabnanny import verbose
from django.db import models
from django.db.models import Sum

from base.models import BaseModel, OrderBaseModel
from members.models import Member
from products.models import Product
from orders.commons import ORDER_STATUS, ORDERSTATUS_CHOICES, PAY_ORGANIZATION, PAY_ORGANIZATION_CHOICES, \
                                PAYMENT_STATUS, PAYMENTSTATUS_CHOICES
from base.commons import DELIVERY_BY, DELIVERY_BY_CHOICES


class CartManager(models.Manager):
    pass


class Cart(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='User')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product')
    payment = models.ForeignKey('Payment', null=True, on_delete=models.CASCADE, verbose_name='Payment')
    order = models.ForeignKey('Order', null=True, on_delete=models.CASCADE, verbose_name='Order')
    quantity = models.IntegerField(null=True, blank=False, verbose_name='Quantity')
    has_order = models.BooleanField(default=False, verbose_name='Has Order ?')
    is_checkout = models.BooleanField(default=False, verbose_name='Is checkout ?')

    objects = CartManager()

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = verbose_name


class OrderManager(models.Manager):
    pass


class Order(OrderBaseModel):
    order_serial_number = models.CharField(null=True, blank=False, unique=True, max_length=200, verbose_name='Order Serial Number')
    user = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='User')
    receiver_name = models.CharField(null=True, blank=False, max_length=50, verbose_name='Receiver Name')
    receiver_phone = models.CharField(null=True, blank=False, max_length=10, verbose_name='Receiver Phone Number')
    shipping_address = models.CharField(null=True, blank=False, max_length=200, verbose_name='Shipping Address')
    city = models.CharField(null=True, blank=False, max_length=20, verbose_name='City')
    post_code = models.CharField(null=True, blank=False, max_length=6, verbose_name='Post Code')
    total_price = models.PositiveIntegerField(null=True, blank=False, verbose_name='Toatal Price')
    comment = models.TextField(null=True, blank=True, max_length=2000, verbose_name='Custom Comment')
    order_status = models.PositiveSmallIntegerField(db_index=True, null=False, default=ORDER_STATUS.NON_SUBMIT, choices=ORDERSTATUS_CHOICES, verbose_name='Order Status')
    delivery_by = models.PositiveSmallIntegerField(db_index=True, default=DELIVERY_BY.NONE, choices=DELIVERY_BY_CHOICES, verbose_name='Delivery By')
    failed_asn = models.BooleanField(default=False, verbose_name='ASN Failed ?')
    is_paid = models.BooleanField(default=False, verbose_name='Is checkout ?')

    objects = OrderManager()

    class Meta:
        verbose_name = 'Order Header'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'The order serial number is : %s' %self.order_serial_number

    def retry_order(self, status):
        if status == ORDER_STATUS.TEMP_ERROR and self.retry_counter < 5:
            self.retry_count += 1
            self.asn_status == ORDER_STATUS.RETRYING
            self.save()
        elif status == ORDER_STATUS.TEMP_ERROR and self.retry_counter == 5:
            self.asn_status == ORDER_STATUS.ORDER_ERROR
            self.save()


class OrderLineManager(models.Manager):
    def sum_order_total_price(self):
        lines = self.order.orderline_set.all()
        return lines.aggregate(total_price=Sum('price'))['total_price']


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Order Header')
    line_no = models.PositiveIntegerField(default=1, null=True, blank=False, verbose_name='Line Number')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product')
    quantity = models.IntegerField(null=True, blank=False, verbose_name='Quantity')

    objects = OrderLineManager()

    class Meta:
        verbose_name = 'Order Line'
        verbose_name_plural = verbose_name
        unique_together = ['order', 'line_no']

    def __str__(self):
        return 'The order number is : {0}, and this is orderline with line number : {1}'.format(self.order.order_number, self.line_no)

    def get_price(self):
        if not self.price and self.product:
            self.price = self.product.price
            self.save()


class Payment(BaseModel):
    user = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='User')
    order = models.OneToOneField('Order', null=True, on_delete=models.CASCADE, verbose_name='Order')
    pay_org = models.PositiveSmallIntegerField(db_index=True, default=PAY_ORGANIZATION.NONE, choices=PAY_ORGANIZATION_CHOICES, verbose_name='Payment Organization')
    card_last_number = models.CharField(null=True, blank=False, max_length=4, verbose_name='Credit Card last four number')
    payment_status = models.PositiveSmallIntegerField(db_index=True, default=PAYMENT_STATUS.NONE, choices=PAYMENTSTATUS_CHOICES, verbose_name='Payment Status')
    total_price = models.PositiveIntegerField(null=True, blank=False, verbose_name='Toatal Price')

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = verbose_name