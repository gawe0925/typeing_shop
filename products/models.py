from django.db import models
from django.utils import timezone

from base.models import ProductBaseModel


class Brand(models.Model):
    brand_name = models.CharField(db_index=True, null=True, blank=False, max_length=128,verbose_name='Brand Name')
    tax_no = models.CharField(null=True, blank=True, max_length=20, verbose_name='Tax Number')
    phone = models.CharField(null=True, blank=True, max_length=20, verbose_name='Phone Number')
    contactor = models.CharField(null=True, blank=True, max_length=20, verbose_name='Contactor')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='Address')
    is_active = models.BooleanField(default=True, verbose_name='Active Brand')

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = verbose_name


class Product(ProductBaseModel):
    product_code = models.AutoField(primary_key=True, default='Typingshop'+'1'.zfill(5), null=False, blank=False, verbose_name='Prodcut Code')
    brand = models.ForeignKey(Brand, null=True, blank=False, on_delete=models.CASCADE, verbose_name='Brand')
    product_name = models.CharField(db_index=True, choices=None, null=True, blank=False, max_length=128, verbose_name='Prodcut Type Name')
    price = models.CharField(db_index=True, null=True, blank=False, max_length=200, verbose_name='Price')
    stock_quantity = models.CharField(default=0, db_index=True, null=False, blank=False, max_length=1024, verbose_name='Stock Quantity')
    unit = models.CharField(null=True, blank=True, max_length=100, verbose_name='Unit', help_text='For instance : Pices or a Package')
    color = models.CharField(null=True, blank=True, max_length=20, verbose_name='Color')
    manufactor = models.CharField(db_index=True, null=True, blank=True, max_length=100, verbose_name='Manufator')
    manufactor_address = models.CharField(null=True, blank=True, max_length=300, verbose_name='Manufactor Address')
    non_returnable = models.BooleanField(default=False, null=False, blank=False, verbose_name='Non Returnable')
    out_of_stock = models.BooleanField(default=False, null=False, blank=False, verbose_name='Out of Stock', help_text='If it is True, then set stock quantity as zero')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{0}'s product_code is : {1}".format(self.product_name, self.product_code)