import re
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from base.tasks import is_authenticated, is_superuser

from asns.apis import get_exist_asn
from asns.models import ASNHeader
from asns.commons import ASN_STATUS
from rest_framework import authentication, permissions


# Detail of ASN
class ASNDetailView(APIView):
    def post(self, request):
        authenticated_result = is_authenticated(self)
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
        
        order_number = data['order_serial_number']

        exist_asn = get_exist_asn(order_number, authenticated_result)

        if type(exist_asn) == dict:
            error, status_code = exist_asn['error']
            return Response(error, status=status_code)
        
        header, lines = exist_asn

        return Response(dict(ASNHeader=dict(order=header.order or '',
                                        user=header.user or '',
                                        receiver_name=header.receiver_name or '',
                                        receiver_phone=header.receiver_phone or '',
                                        shipping_address=header.shipping_address or '',
                                        city=header.city or '',
                                        post_code=header.post_code or '',
                                        asn_serial_number=header.asn_serial_number or '',
                                        error_message=header.error_message or '',
                                        asn_status=header.asn_status or '',
                                        delivery_by=header.delivery_by or '',
                                        feedback=header.feedback or '',
                                        reply=header.reply or '',
                                        ASNLine=[dict(header=line.header or '',
                                                asn_line_no=line.asn_line_no or '',
                                                order_line=line.order_line or '',
                                                product=line.product or '',
                                                quantity=line.quantity or '') 
                                                for line in lines])),
                                        status=200)


# while staff process ASN and send product out, then update ASN
class UpdateReadyASN(APIView):
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
            data['asn_serial_number']
        except:
            return Response({"error":"none data"}, status=400)
        
        asn_numbers = data['asn_serial_number']

        exist_asn = ASNHeader.objects.filter(asn_serial_number__in=asn_numbers)

        if not exist_asn:
            return Response({"error":"ASN not found"}, status=400)
        
        exist_asn.update(asn_status=ASN_STATUS.READY_TO_DELIVERY)


class UpdateASNStatusView(APIView):
    def post(self, requset):
        token = self.request.headers.get('Authorization')
        if not token:
            return Response({"error":"access deny"}, status=403)
                
        try:
            self.request.data
        except:
            return Response({"error":"none data"}, status=400)
        
        data = self.request.data

        try:
            data['update_asn']
        except:
            return Response({"error":"none data"}, status=400)

        update_asns = data['update_asn']

        update_counter = 0
        for update_asn in update_asns:
            serial_number, status_code = update_asn

            exist_asn = ASNHeader.objects.exclude(asn_status__lt=ASN_STATUS.READY_TO_DELIVERY
                                                ).filter(asn_serial_number=serial_number)
        
            if not exist_asn:
                return Response({"error":"asn not found"})
        
            update_asn = exist_asn.update(asn_status=status_code)
            update_counter += update_asn

        return Response({"success":"update {0} of {1}".format(update_counter, len(update_asns))})