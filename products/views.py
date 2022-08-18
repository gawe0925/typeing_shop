from django.shortcuts import render
from django.db.models import Sum, F
from rest_framework.views import APIView
from rest_framework.response import Response

from base.tasks import is_authenticated, is_superuser
from products.models import Brand, Product


class CreateBrandView(APIView):
    def post(self, request):
        authenticated_result = is_superuser(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)

        try:
            self.request.data
        except:
            return Response({"error" : "none data"}, status=400)
        
        data = self.request.data
        
        try:
            data['brand']
        except:
            return Response({"error" : "none data"}, status=400)
        
        brands = data['brand']

        brand_list = []
        for brand in brands:
            brand_list.append(Brand(
                            brand_name=brand['brand_name'],
                            tax_no=brand['tax_no'],
                            phone=brand['phone'],
                            contactor=brand['contactor'],
                            address=brand['address'])
                            )
        if not brand_list:
            return Response({"error" : "failed to create brand's object before bulk_create"}, 
                            status=500)
        
        new_brands = Brand.objects.bulk_create(brand_list)

        if not new_brands:
            return Response({"error" : "failed to create new brand"}, status=500)

        return Response({"new_brand" : [{
                                        "brand_id" : new_brand.brand_id,
                                        "brand_name" : new_brand.brand_name,
                                        "tax_no" : new_brand.tax_no or '',
                                        "phone" : new_brand.phone or '',
                                        "contactor" : new_brand.contactor or '',
                                        "address" : new_brand.address or '',
                                        "active" : new_brand.is_active,
                                        "Message" : "Created new brand"
                                        } for new_brand in new_brands]
                                        }, status=200)


class CreateProductView(APIView):
    def post(self, request):
        authenticated_result = is_superuser(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        try:
            self.request.data
        except:
            return Response({"error":"none data"}, status=400)
        
        data = self.request.data

        try:
            data['product']
        except:
            return Response({"error":"none data"}, status=400)

        products = data['product']
        product_lsit = []
        for product in products:
            product_lsit.append(Product(
                                product_code=product['product_code'],
                                brand=product['brand'],
                                product_name=product['product_name'],
                                price=product['price'],
                                stock_quantity=product['stock_quantity'],
                                unit=product['unit'],
                                color=product['color'],
                                manufactor=product['manufactor'],
                                manufactor_address=product['manufactor_address'],
                                non_returnable=product['non_returnable']))
        if not product_lsit:
            return Response({"error" : "failed to create product's object before bulk_create"}, 
                            status=500)
        
        new_product = Product.objects.bulk_create(product_lsit)

        if not new_product:
            return Response({"error" : "failed to create new product"}, status=500)

        return Response({"new_product" : [dict(product_code=product.product_code,
                                            brand=product.brand,
                                            product_name=product.product_name,
                                            price=product.price,
                                            stock_quantity=product.stock_quantity,
                                            unit=product.unit,
                                            color=product.color,
                                            manufactor=product.manufactor,
                                            manufactor_address=product.manufactor_address,
                                            non_returnable=product.non_returnable)
                                            for product in new_product]})


# out of stock API
class OutOfStockView(APIView):
    def post(self, request):
        authenticated_result = is_superuser(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        try:
            self.request.date
        except:
            return Response({"error":"none data"})
        
        data = self.request.date

        try:
            data['product']
        except:
            return Response({"error":"none data"}, status=400)

        products = data['product']
        update_list = []
        for product in products:
            if product['product_code'] not in update_list:
                update_list.append(product['product_code'])
        
        update_products = Product.objects.filter(product_code__in=update_list,
                                                out_of_stock=False)
        for update_product in update_products:
            update_product.out_of_stock = True
        
        update_count = Product.objects.bulk_update(update_products, ['out_of_stock'])
        
        if update_count == 0:
            return Response({"result":"updated 0 out of %s" %len(products)}, status=500)
        return Response({"result":"updated {0} out of {1}".format(update_count,len(products))}, status=200)


# product invalid API
class DeleteProductView(APIView):
    def post(self, request):
        # only superuser can delete
        authenticated_result = is_superuser(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        try:
            self.request.date
        except:
            return Response({"error":"none data"})

        data = self.request.date

        try:
            data['delete_product']
        except:
            return Response({"error":"none data"}, status=400)

        products = data['delete_product']
        update_list = []
        for product in products:
            if product['product_code'] not in update_list:
                update_list.append(product['product_code'])
        
        update_products = Product.objects.filter(product_code__in=update_list,
                                                is_available=True)
        for update_product in update_products:
            update_product.is_available = False
        
        update_count = Product.objects.bulk_update(update_products, ['is_available'])
        
        if update_count == 0:
            return Response({"result":"updated 0 out of %s" %len(products)}, status=500)
        return Response({"result":"updated {0} out of {1}".format(update_count,len(products))}, status=200)


# access product's information
class ProductDetailsView(APIView):
    def get(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)
        
        valid_products = Product.objects.filter(is_available=True).order_by('out_of_stock','id')
        
        return Response({"product_information":[dict(product_code=product.product_code,
                                                brand=product.brand,
                                                product_name=product.product_name,
                                                price=product.price,
                                                stock_quantity=product.stock_quantity,
                                                unit=product.unit,
                                                color=product.color,
                                                manufactor=product.manufactor,
                                                manufactor_address=product.manufactor_address,
                                                non_returnable=product.non_returnable,
                                                out_of_stock=product.out_of_stock,
                                                ) for product in valid_products]}, status=200)