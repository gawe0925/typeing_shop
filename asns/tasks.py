from ty import celery_app

from orders.models import Order
from orders.commons import ORDER_STATUS

from asns.commons import ASN_STATUS
from asns.models import ASNHeader, ASNLine

def get_exist_asn(order_number, authenticated_result):
    exist_order = Order.objects.filter(order_serial_number=order_number).distinct().first()

    if not exist_order:
        return {"error":({"error":"order not found"}, 400)}
    
    if exist_order.user != authenticated_result:
        return {"error":({"error":"access deny"}, 403)}

    # failed to create asn, need to review asn's status
    if exist_order.failed_asn:
        return {"error":({"error":"asn_er__001"}, 400)}
    
    # payment required
    if not exist_order.is_paid:
        return {"error":({"error":"cash out yet"}, 402)}
    
    asnheader = exist_order.asnheader_set.first() or []
    asnlines = asnheader.asnline_set.all() or []

    return (asnheader, asnlines)

def create_asn(orders):
    order_id_list = []
    order_list = []
    for order in orders:
        if order.id not in order_id_list:
            order_id_list.append(order.id)
        orderline = order.orderline_set.all().distinct()
        if (order, orderline) not in order_list:
            order_list.append((order, orderline))

    for object in order_list:
        order, order_lines = object
        # get ASNHeader object
        asnheader = ASNHeader()
        new_serial_number = asnheader.new_asn_document_no()

        created_header = ASNHeader.objects.create(order=order,
                                                user=order.user,
                                                receiver_name=order.receiver_name,
                                                receiver_phone=order.receiver_phone,
                                                shipping_address=order.shipping_address,
                                                city=order.city,
                                                post_code=order.post_code,
                                                asn_serial_number=new_serial_number,
                                                asn_status=ASN_STATUS.NEW,
                                                delivery_by=order.delivery_by)
        if not created_header:
            order.failed_asn = True
            order.save()
        else:
            asnline = []
            for order_line in order_lines:
                asnline.append(ASNLine(header=created_header,
                                        asn_line_no=order_line.line_no,
                                        order_line=order_line,
                                        product=order_line.product,
                                        quantity=order_line.quantity))
            
            created_lines = ASNLine.objects.bulk_create(asnline)

            if not created_lines:
                created_header.asn_status = ASN_STATUS.ASN_ERROR
                order.failed_asn = True
                created_header.save()
                order.save()
            else:
                created_header.asn_status = ASN_STATUS.READY_TO_DELIVERY
                created_header.save()
    
    asn_result = Order.objects.filter(id__in=order_id_list, failed_asn=False)
    if not asn_result:
        return False
    return True

@celery_app.task(name='tasks.asn_control',
                 bind=True)
def asn_control(self):
    orders = list(Order.objects.filter(is_paid=True, failed_asn=False, 
                                        order_status=ORDER_STATUS.SUBMIT))
    if not orders:
        return False

    task_reslut = create_asn(orders)
    if not task_reslut:
        return False
    return True