from django.db import models
from django.utils import timezone

from asns.commons import ASN_STATUS, ASN_STATUS_CHOICES
from base.commons import DELIVERY_BY, DELIVERY_BY_CHOICES
from orders.models import Order, OrderLine
from base.models import ASNBaseModel
from products.models import Product
from members.models import Member


class ASNHeaderManager(models.Manager):
    pass


class ASNHeader(ASNBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Order')
    user = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='User')
    receiver_name = models.CharField(null=True, blank=False, max_length=50, verbose_name='Receiver Name')
    receiver_phone = models.CharField(null=True, blank=False, max_length=10, verbose_name='Receiver Phone Number')
    shipping_address = models.CharField(null=True, blank=False, max_length=200, verbose_name='Shipping Address')
    city = models.CharField(null=True, blank=False, max_length=20, verbose_name='City')
    post_code = models.CharField(null=True, blank=False, max_length=6, verbose_name='Post Code')
    asn_serial_number = models.CharField(null=True, blank=False, unique=True, max_length=100, verbose_name='Shipment Serial Number')
    error_message = models.CharField(null=True, blank=True, max_length=2048, verbose_name='Error Message')
    asn_status = models.PositiveSmallIntegerField(db_index=True, default=ASN_STATUS.NEW, choices=ASN_STATUS_CHOICES, verbose_name='ASN Status')
    delivery_by = models.PositiveSmallIntegerField(db_index=True, default=DELIVERY_BY.NONE, choices=DELIVERY_BY_CHOICES, verbose_name='Delivery By')
    feedback = models.TextField(null=True, blank=True, max_length=2000, verbose_name='Custom Feedback')
    reply = models.TextField(null=True, blank=True, max_length=2000, verbose_name='Feedback Reply')

    objects = ASNHeaderManager()

    class Meta:
        verbose_name = 'ASN Header'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'The ASN serial number is : %s' %self.asn_serial_number

    def new_asn_document_no(self):
        if not self.asn_serial_number:
            now = timezone.now()
            number_prefix = now.strftime('%Y%m%d')
            
            db_serial = str(ASNHeader.objects.filter(asn_serial_number__startswith=number_prefix).count() + 1)

            asn_serial_number = number_prefix + db_serial.zfill(5)

            return str(asn_serial_number)


class ASNLine(ASNBaseModel):
    header = models.ForeignKey(ASNHeader, on_delete=models.CASCADE, verbose_name='ASN Header')
    asn_line_no = models.PositiveSmallIntegerField(default=1, null=False, blank=False, verbose_name='ASNLine Line Number')
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, verbose_name='Order Line')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product')
    quantity = models.IntegerField(null=True, blank=False, verbose_name='Quantity')

    class Meta:
        verbose_name = 'ASN Line'
        verbose_name_plural = verbose_name
        unique_together = ['header', 'asn_line_no']

    def return_process(self):
        if self.product.non_returnable:
            self.error_message = 'This product is non returnable !'
            pass
        else:
            self.is_return == True
            self.save()